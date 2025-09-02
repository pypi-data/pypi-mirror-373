## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">Login</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>
    .wutta-page-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    .wutta-logo {
        margin-top: 2rem;
        display: flex;
        justify-content: center;
    }
    .wutta-logo img {
        max-height: 480px;
        max-width: 640px;
    }
  </style>
</%def>

<%def name="page_content()">
  <div class="wutta-page-content">
    <div class="wutta-logo">${base_meta.full_logo(image_url or None)}</div>
    <div class="card">
      <div class="card-content">
        ${form.render_vue_tag()}
      </div>
    </div>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}Data.usernameInput = null

    ${form.vue_component}.mounted = function() {
        this.$refs.username.focus()
        this.usernameInput = this.$refs.username.$el.querySelector('input')
        this.usernameInput.addEventListener('keydown', this.usernameKeydown)
    }

    ${form.vue_component}.beforeDestroy = function() {
        this.usernameInput.removeEventListener('keydown', this.usernameKeydown)
    }

    ${form.vue_component}.methods.usernameKeydown = function(event) {
        if (event.which == 13) { // ENTER
            event.preventDefault()
            this.$refs.password.focus()
        }
    }

  </script>
</%def>
