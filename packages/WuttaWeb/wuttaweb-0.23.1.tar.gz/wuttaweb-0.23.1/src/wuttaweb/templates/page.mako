## -*- coding: utf-8; -*-
<%inherit file="/base.mako" />

<%def name="page_layout()">
  ${self.page_content()}
</%def>

<%def name="page_content()"></%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${self.render_vue_template_this_page()}
  ${self.render_vue_script_this_page()}
</%def>

<%def name="render_vue_template_this_page()">
  <script type="text/x-template" id="this-page-template">
    <div class="wutta-page-content-wrapper">
      ${self.page_layout()}
    </div>
  </script>
</%def>

<%def name="render_vue_script_this_page()">
  <script>

    const ThisPage = {
        template: '#this-page-template',
        mixins: [WuttaRequestMixin],
        props: {
            ## configureFieldsHelp: Boolean,
        },
        computed: {},
        watch: {},
        methods: {

            changeContentTitle(newTitle) {
                this.$emit('change-content-title', newTitle)
            },
        },
    }

    const ThisPageData = {}

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    ThisPage.data = function() { return ThisPageData }
    Vue.component('this-page', ThisPage)
    <% request.register_component('this-page', 'ThisPage') %>
  </script>
</%def>
