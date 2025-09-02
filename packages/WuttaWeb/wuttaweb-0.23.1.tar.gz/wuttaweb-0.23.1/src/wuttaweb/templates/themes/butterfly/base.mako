## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/base.mako" />
<%namespace file="/http-plugin.mako" import="make_http_plugin" />
<%namespace file="/buefy-plugin.mako" import="make_buefy_plugin" />
<%namespace file="/buefy-components.mako" import="make_buefy_components" />

<%def name="core_javascript()">
  <script type="importmap">
    {
        "imports": {
            "vue": "${h.get_liburl(request, 'bb_vue')}",
            "@oruga-ui/oruga-next": "${h.get_liburl(request, 'bb_oruga')}",
            "@oruga-ui/theme-bulma": "${h.get_liburl(request, 'bb_oruga_bulma')}",
            "@fortawesome/fontawesome-svg-core": "${h.get_liburl(request, 'bb_fontawesome_svg_core')}",
            "@fortawesome/free-solid-svg-icons": "${h.get_liburl(request, 'bb_free_solid_svg_icons')}",
            "@fortawesome/vue-fontawesome": "${h.get_liburl(request, 'bb_vue_fontawesome')}"
        }
    }
  </script>
  <script>
    ## nb. empty stub to avoid errors for older buefy templates
    const Vue = {
        component(tagname, classname) {},
    }
  </script>
</%def>

<%def name="core_styles()">
  ${h.stylesheet_link(h.get_liburl(request, 'bb_oruga_bulma_css'))}
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${make_buefy_components()}
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>
    html, body, .navbar, .footer {
        background-color: LightYellow;
    }
  </style>
</%def>

<%def name="make_vue_app()">
  ${make_http_plugin()}
  ${make_buefy_plugin()}
  <script type="module">
    import { createApp } from 'vue'
    import { Oruga } from '@oruga-ui/oruga-next'
    import { bulmaConfig } from '@oruga-ui/theme-bulma'
    import { library } from "@fortawesome/fontawesome-svg-core"
    import { fas } from "@fortawesome/free-solid-svg-icons"
    import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
    library.add(fas)

    const app = createApp()
    app.component('vue-fontawesome', FontAwesomeIcon)

    % if hasattr(request, 'wuttaweb_registered_components'):
        % for tagname, classname in request.wuttaweb_registered_components.items():
            app.component('${tagname}', ${classname})
        % endfor
    % endif

    app.use(Oruga, {
        ...bulmaConfig,
        iconComponent: 'vue-fontawesome',
        iconPack: 'fas',
    })

    app.use(HttpPlugin)
    app.use(BuefyPlugin)

    app.mount('#app')
  </script>
</%def>
