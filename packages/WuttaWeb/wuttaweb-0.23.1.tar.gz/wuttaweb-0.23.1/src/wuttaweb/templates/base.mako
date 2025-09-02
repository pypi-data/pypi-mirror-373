## -*- coding: utf-8; -*-
<%namespace name="base_meta" file="/base_meta.mako" />
<%namespace file="/wutta-components.mako" import="make_wutta_components" />
<!DOCTYPE html>
<html lang="en">
  ${self.html_head()}
  <body>
    <div id="app" style="height: 100%;">
      <whole-page />
    </div>

    ## nb. sometimes a template needs to define something
    ## before the body content proper is rendered
    ${self.before_content()}

    ## content body from derived/child template
    ${self.body()}

    ## Vue app
    ${self.render_vue_templates()}
    ${self.modify_vue_vars()}
    ${self.make_vue_components()}
    ${self.make_vue_app()}
  </body>
</html>

<%def name="html_head()">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>${self.head_title()}</title>
    ${base_meta.favicon()}
    ${self.header_core()}
    ${self.head_tags()}
  </head>
</%def>

## nb. this is the full <title> within html <head>
<%def name="head_title()">${base_meta.global_title()} &raquo; ${self.title()}</%def>

## nb. this becomes part of head_title() above
## it also is used as default value for content_title() below
<%def name="title()"></%def>

## nb. this is the "content title" as shown on screen, within the
## "hero bar" just below the "index title"
<%def name="content_title()">${self.title()}</%def>

<%def name="header_core()">
  ${self.base_javascript()}
  ${self.extra_javascript()}
  ${self.base_styles()}
  ${self.extra_styles()}
</%def>

<%def name="core_javascript()">
  ${self.vuejs()}
  ${self.buefy()}
  ${self.fontawesome()}
</%def>

<%def name="base_javascript()">
  ${self.core_javascript()}
  ${self.hamburger_menu_js()}
</%def>

<%def name="hamburger_menu_js()">
  <script>

    ## NOTE: this code was copied from
    ## https://bulma.io/documentation/components/navbar/#navbar-menu

    document.addEventListener('DOMContentLoaded', () => {

        // Get all "navbar-burger" elements
        const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0)

        // Add a click event on each of them
        $navbarBurgers.forEach( el => {
            el.addEventListener('click', () => {

                // Get the target from the "data-target" attribute
                const target = el.dataset.target
                const $target = document.getElementById(target)

                // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
                el.classList.toggle('is-active')
                $target.classList.toggle('is-active')

            })
        })
    })

  </script>
</%def>

<%def name="vuejs()">
  ${h.javascript_link(h.get_liburl(request, 'vue'))}
  ${h.javascript_link(h.get_liburl(request, 'vue_resource'))}
</%def>

<%def name="buefy()">
  ${h.javascript_link(h.get_liburl(request, 'buefy'))}
</%def>

<%def name="fontawesome()">
  <script defer src="${h.get_liburl(request, 'fontawesome')}"></script>
</%def>

<%def name="extra_javascript()"></%def>

<%def name="core_styles()">
  ${self.buefy_styles()}
</%def>

<%def name="buefy_styles()">
  ${h.stylesheet_link(h.get_liburl(request, 'buefy.css'))}
</%def>

<%def name="base_styles()">
  ${self.core_styles()}
  <style>

    ##############################
    ## page
    ##############################

    ## nb. helps force footer to bottom of screen
    html, body {
        height: 100%;
    }

    % if not request.wutta_config.production():
        html, body, .navbar, .footer {
          background-image: url(${request.static_url('wuttaweb:static/img/testing.png')});
        }
    % endif

    ## nb. this refers to the "home link" app title, next to small
    ## header logo in top left of screen
    #navbar-brand-title {
        font-weight: bold;
        margin-left: 0.3rem;
    }

    #header-index-title {
        display: flex;
        gap: 1.5rem;
        padding-left: 0.5rem;
    }

    h1.title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0 !important;
    }

    #content-title h1 {
        max-width: 95%;
        overflow: hidden;
        padding-left: 0.5rem;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .wutta-page-content-wrapper {
        height: 100%;
    }

    ##############################
    ## grids
    ##############################

    .wutta-filter {
        display: flex;
        gap: 0.5rem;
    }

    .wutta-filter .button.filter-toggle,
    .wutta-filter .filter-verb {
        justify-content: left;
        min-width: 15rem;
    }

    .wutta-filter .filter-verb .select,
    .wutta-filter .filter-verb .select select {
        width: 100%;
    }

    .wutta-grid-tools-wrapper {
        display: flex;
        gap: 0.5rem;
    }

    ##############################
    ## forms
    ##############################

    .wutta-form-wrapper {
        margin-left: 5rem;
        margin-top: 2rem;
        width: 50%;
    }

    .wutta-form-wrapper .field.is-horizontal .field-body .select,
    .wutta-form-wrapper .field.is-horizontal .field-body .select select {
        width: 100%;
    }

    .tool-panels-wrapper {
        padding: 1rem;
    }

  </style>
</%def>

<%def name="extra_styles()">
  ${base_meta.extra_styles()}
</%def>

<%def name="head_tags()"></%def>

<%def name="whole_page_content()">
      ## nb. the header-wrapper contains 2 elements:
      ## 1) header proper (menu + index title area)
      ## 2) page/content title area
      <div class="header-wrapper">

        ## nb. the header proper contains 2 elements:
        ## 1) menu bar
        ## 2) index title area
        <header>

          ## nb. this is the main menu bar
          <nav class="navbar" role="navigation" aria-label="main navigation">
            ${self.render_navbar_brand()}
            ${self.render_navbar_menu()}
          </nav>

          ## nb. this is the "index title" area
          <nav class="level" style="margin: 0.5rem 0.5rem 0.5rem auto;">

            ## nb. this is the index title proper
            <div class="level-left">
              <div id="header-index-title" class="level-item">
                % if index_title:
                    % if index_url:
                        <h1 class="title">${h.link_to(index_title, index_url)}</h1>
                    % else:
                        <h1 class="title">${index_title}</h1>
                    % endif
                    ${self.index_title_controls()}
                % endif
              </div>
            </div>

            ## nb. this is a utility area for the master context
            <div class="level-right">

              ## Configure button
              % if master and master.configurable and not master.configuring and master.has_perm('configure'):
                  <div class="level-item">
                    <wutta-button once type="is-primary"
                                  tag="a" href="${url(f'{route_prefix}.configure')}"
                                  icon-left="cog"
                                  label="Configure" />
                  </div>
              % endif

              ${self.render_theme_picker()}
              ${self.render_feedback_button()}

            </div>
          </nav>
        </header>

        ## nb. the page / content title area (aka. hero bar)
        % if capture(self.content_title):
            <section id="content-title"
                     class="has-background-primary">
              <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem;">

                <div style="width: 60%; display: flex; gap: 0.5rem;">

                  <h1 class="title has-text-white"
                      v-html="contentTitleHTML">
                  </h1>

                  <div style="display: flex; gap: 0.5rem;">
                    ${self.render_instance_header_title_extras()}
                  </div>

                </div>

                <div style="width: 40%; display: flex; gap: 0.5rem;">
                  ${self.render_instance_header_buttons()}
                </div>

              </div>
            </section>
        % endif

      </div> <!-- header-wrapper -->

      ## nb. the page content area
      <div class="content-wrapper"
           style="flex-grow: 1; padding: 0.5rem;">
        <section id="page-body" style="height: 100%;">

          % if request.session.peek_flash('error'):
              % for error in request.session.pop_flash('error'):
                  <b-notification type="is-warning">
                    ${error}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash('warning'):
              % for msg in request.session.pop_flash('warning'):
                  <b-notification type="is-warning">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash():
              % for msg in request.session.pop_flash():
                  <b-notification type="is-info">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          <div style="height: 100%;">
            ${self.render_this_page_component()}
          </div>
        </section>
      </div><!-- content-wrapper -->

      ## nb. the page footer
      <footer class="footer">
        <div class="content">
          ${base_meta.footer()}
        </div>
      </footer>
</%def>

<%def name="index_title_controls()">
  % if master and master.creatable and not master.creating and master.has_perm('create'):
      <wutta-button once type="is-primary"
                    tag="a" href="${url(f'{route_prefix}.create')}"
                    icon-left="plus"
                    label="Create New" />
  % endif
</%def>

<%def name="render_vue_template_whole_page()">
  <script type="text/x-template" id="whole-page-template">

    ## nb. the whole-page normally contains 3 elements:
    ## 1) header-wrapper
    ## 2) content-wrapper
    ## 3) footer
    <div id="whole-page"
         style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
      ${self.whole_page_content()}
    </div>
  </script>
</%def>

<%def name="render_navbar_brand()">
  <div class="navbar-brand">
    <a class="navbar-item" href="${url('home')}">
      <div style="display: flex; align-items: center;">
        ${base_meta.header_logo()}
        <div id="navbar-brand-title">
          ${base_meta.global_title()}
        </div>
      </div>
    </a>
    <a role="button" class="navbar-burger" data-target="navbar-menu" aria-label="menu" aria-expanded="false">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>
</%def>

<%def name="render_navbar_menu()">
  <div class="navbar-menu" id="navbar-menu">
    ${self.render_navbar_start()}
    ${self.render_navbar_end()}
  </div>
</%def>

<%def name="render_navbar_start()">
  <div class="navbar-start">

    % for topitem in menus:
        % if topitem['is_link']:
            ${h.link_to(topitem['title'], topitem['url'], target=topitem['target'], class_='navbar-item')}
        % else:
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">${topitem['title']}</a>
              <div class="navbar-dropdown">
                % for item in topitem['items']:
                    % if item['is_menu']:
                        <% item_hash = id(item) %>
                        <% toggle = 'menu_{}_shown'.format(item_hash) %>
                        <div>
                          <a class="navbar-link" @click.prevent="toggleNestedMenu('${item_hash}')">
                            ${item['title']}
                          </a>
                        </div>
                        % for subitem in item['items']:
                            % if subitem['is_sep']:
                                <hr class="navbar-divider" v-show="${toggle}">
                            % else:
                                ${h.link_to("{}".format(subitem['title']), subitem['url'], class_='navbar-item nested', target=subitem['target'], **{'v-show': toggle})}
                            % endif
                        % endfor
                    % else:
                        % if item['is_sep']:
                            <hr class="navbar-divider">
                        % else:
                            ${h.link_to(item['title'], item['url'], class_='navbar-item', target=item['target'])}
                        % endif
                    % endif
                % endfor
              </div>
            </div>
        % endif
    % endfor

  </div>
</%def>

<%def name="render_navbar_end()">
  <div class="navbar-end">
    ${self.render_user_menu()}
  </div>
</%def>

<%def name="render_theme_picker()">
  % if expose_theme_picker and request.has_perm('common.change_theme'):
      <div class="level-item">
        ${h.form(url('change_theme'), method='POST', ref='themePickerForm')}
          ${h.csrf_token(request)}
          <input type="hidden" name="referrer" :value="referrer" />
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>Theme:</span>
            <${b}-select name="theme"
                      v-model="globalTheme"
                      @input="changeTheme()">
              % for name in available_themes:
                  <option value="${name}">${name}</option>
              % endfor
            </${b}-select>
          </div>
        ${h.end_form()}
      </div>
  % endif

</%def>

<%def name="render_feedback_button()">
  % if request.has_perm('common.feedback'):
      <wutta-feedback-form action="${url('feedback')}" />
  % endif
</%def>

<%def name="render_vue_template_feedback()">
  <script type="text/x-template" id="wutta-feedback-template">
    <div>

      <b-button type="is-primary"
                @click="showFeedback()"
                icon-pack="fas"
                icon-left="comment">
        Feedback
      </b-button>

      <${b}-modal has-modal-card
                  :active.sync="showDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">User Feedback</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              Feedback regarding this website may be submitted below.
            </p>

            <b-field label="User Name"
                     :type="userName && userName.trim() ? null : 'is-danger'">
              <b-input v-model="userName"
                       % if request.user:
                           disabled
                       % endif
                       expanded />
            </b-field>

            <b-field label="Referring URL">
              <b-input v-model="referrer"
                       disabled="true"
                       expanded />
            </b-field>

            <b-field label="Message"
                     :type="message && message.trim() ? null : 'is-danger'">
              <b-input type="textarea"
                       v-model="message"
                       ref="textarea"
                       expanded />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <div style="display: flex; gap: 0.5rem;">
            <b-button @click="showDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="paper-plane"
                      @click="sendFeedback()"
                      :disabled="submitDisabled">
              {{ sendingFeedback ? "Working, please wait..." : "Send Message" }}
            </b-button>
            </div>
          </footer>
        </div>
      </${b}-modal>

    </div>
  </script>
</%def>

<%def name="render_vue_script_feedback()">
  <script>

    const WuttaFeedbackForm = {
        template: '#wutta-feedback-template',
        mixins: [WuttaRequestMixin],
        props: {
            action: String,
        },
        computed: {

            submitDisabled() {
                if (this.sendingFeedback) {
                    return true
                }
                if (!this.userName || !this.userName.trim()) {
                    return true
                }
                if (!this.message || !this.message.trim()) {
                    return true
                }
                return false
            },
        },
        methods: {

            showFeedback() {
                // nb. update referrer to include anchor hash if any
                this.referrer = location.href
                this.showDialog = true
                this.$nextTick(function() {
                    this.$refs.textarea.focus()
                })
            },

            getParams() {
                return {
                    referrer: this.referrer,
                    user_uuid: this.userUUID,
                    user_name: this.userName.trim(),
                    message: this.message.trim(),
                    ...this.getExtraParams(),
                }
            },

            getExtraParams() {},

            sendFeedback() {
                this.sendingFeedback = true
                const params = this.getParams()
                this.wuttaPOST(this.action, params, response => {

                    this.$buefy.toast.open({
                        message: "Message sent!  Thank you for your feedback.",
                        type: 'is-info',
                        duration: 4000, // 4 seconds
                    })

                    this.showDialog = false
                    // clear out message, in case they need to send another
                    this.message = ""
                    this.sendingFeedback = false

                }, response => { // failure
                    this.sendingFeedback = false
                })
            },
        }
    }

    const WuttaFeedbackFormData = {
        referrer: null,
        userUUID: ${json.dumps(request.user.uuid.hex if request.user else None)|n},
        userName: ${json.dumps(str(request.user) if request.user else None)|n},
        showDialog: false,
        sendingFeedback: false,
        message: '',
    }

  </script>
</%def>

<%def name="render_vue_script_whole_page()">
  <script>

    const WholePage = {
        template: '#whole-page-template',
        mixins: [WuttaRequestMixin],
        computed: {},

        mounted() {
            for (let hook of this.mountedHooks) {
                hook.call(this)
            }
        },

        methods: {

            changeContentTitle(newTitle) {
                this.contentTitleHTML = newTitle
            },

            toggleNestedMenu(hash) {
                const key = 'menu_' + hash + '_shown'
                this[key] = !this[key]
            },

            % if request.is_admin:

                startBeingRoot() {
                    this.$refs.startBeingRootForm.submit()
                },

                stopBeingRoot() {
                    this.$refs.stopBeingRootForm.submit()
                },

            % endif

            % if expose_theme_picker and request.has_perm('common.change_theme'):
                changeTheme() {
                    this.$refs.themePickerForm.submit()
                },
            % endif
        },
    }

    const WholePageData = {
        contentTitleHTML: ${json.dumps(capture(self.content_title))|n},
        referrer: location.href,
        mountedHooks: [],

        % if expose_theme_picker and request.has_perm('common.change_theme'):
            globalTheme: ${json.dumps(theme or None)|n},
        % endif
    }

    ## declare nested menu visibility toggle flags
    % for topitem in menus:
        % if topitem['is_menu']:
            % for item in topitem['items']:
                % if item['is_menu']:
                    WholePageData.menu_${id(item)}_shown = false
                % endif
            % endfor
        % endif
    % endfor

  </script>
</%def>

<%def name="before_content()"></%def>

<%def name="render_this_page_component()">
  <this-page @change-content-title="changeContentTitle" />
</%def>

<%def name="render_user_menu()">
  % if request.user:
      <div class="navbar-item has-dropdown is-hoverable">
        <a class="navbar-link ${'has-background-danger has-text-white' if request.is_root else ''}">${request.user}</a>
        <div class="navbar-dropdown">
          % if request.is_root:
              ${h.form(url('stop_root'), ref='stopBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.url}" />
              <a @click="stopBeingRoot()"
                 class="navbar-item has-background-danger has-text-white">
                Stop being root
              </a>
              ${h.end_form()}
          % elif request.is_admin:
              ${h.form(url('become_root'), ref='startBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.url}" />
              <a @click="startBeingRoot()"
                 class="navbar-item has-background-danger has-text-white">
                Become root
              </a>
              ${h.end_form()}
          % endif
          % if request.is_root or not request.user.prevent_edit:
              ${h.link_to("Change Password", url('change_password'), class_='navbar-item')}
          % endif
          ${h.link_to("Logout", url('logout'), class_='navbar-item')}
        </div>
      </div>
  % else:
      ${h.link_to("Login", url('login'), class_='navbar-item')}
  % endif
</%def>

<%def name="render_instance_header_title_extras()"></%def>

<%def name="render_instance_header_buttons()">
  ${self.render_crud_header_buttons()}
  ${self.render_prevnext_header_buttons()}
</%def>

<%def name="render_crud_header_buttons()">
  % if master:
      % if master.viewing:
          % if master.editable and instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
          % if master.deletable and instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.editing:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if master.deletable and instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.deleting:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if master.editable and instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
      % endif
  % endif
</%def>

<%def name="render_prevnext_header_buttons()"></%def>

##############################
## vue components + app
##############################

<%def name="render_vue_templates()">

  ## nb. must make wutta components first; they are stable so
  ## intermediate pages do not need to modify them.  and some pages
  ## may need the request mixin to be defined.
  ${make_wutta_components()}

  ${self.render_vue_template_whole_page()}
  ${self.render_vue_script_whole_page()}
  % if request.has_perm('common.feedback'):
      ${self.render_vue_template_feedback()}
      ${self.render_vue_script_feedback()}
  % endif
</%def>

<%def name="modify_vue_vars()"></%def>

<%def name="make_vue_components()">
  <script>
    WholePage.data = function() { return WholePageData }
    Vue.component('whole-page', WholePage)
    <% request.register_component('whole-page', 'WholePage') %>
  </script>
  % if request.has_perm('common.feedback'):
      <script>
        WuttaFeedbackForm.data = function() { return WuttaFeedbackFormData }
        Vue.component('wutta-feedback-form', WuttaFeedbackForm)
        <% request.register_component('wutta-feedback-form', 'WuttaFeedbackForm') %>
      </script>
  % endif
</%def>

<%def name="make_vue_app()">
  <script>
    new Vue({
        el: '#app'
    })
  </script>
</%def>
