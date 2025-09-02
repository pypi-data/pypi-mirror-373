## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="page_content()">

  <nav class="panel">
    <p class="panel-heading">Application</p>
    <div class="panel-block">
      <div style="width: 100%;">
        <b-field horizontal label="Distribution">
          <span>${app.get_distribution() or f'?? - set config for `{app.appname}.app_dist`'}</span>
        </b-field>
        <b-field horizontal label="Version">
          <span>${app.get_version() or f'?? - set config for `{app.appname}.app_dist`'}</span>
        </b-field>
        <b-field horizontal label="App Title">
          <span>${app.get_title()}</span>
        </b-field>
        <b-field horizontal label="Node Title">
          <span>${app.get_node_title()}</span>
        </b-field>
        <b-field horizontal label="Production Mode">
          <span>${"Yes" if config.production() else "No"}</span>
        </b-field>
        <b-field horizontal label="Email Enabled">
          <span>${"Yes" if app.get_email_handler().sending_is_enabled() else "No"}</span>
        </b-field>
      </div>
    </div>
  </nav>

  <nav class="panel">
    <p class="panel-heading">Configuration Files</p>
    <div class="panel-block">
      <div style="width: 100%;">
        <${b}-table :data="configFiles">

          <${b}-table-column field="priority"
                          label="Priority"
                          v-slot="props">
            {{ props.row.priority }}
          </${b}-table-column>

          <${b}-table-column field="path"
                          label="File Path"
                          v-slot="props">
            {{ props.row.path }}
          </${b}-table-column>

        </${b}-table>
      </div>
    </div>
  </nav>

  <${b}-collapse class="panel"
                 :open="false"
                 @open="openInstalledPackages">

    <template #trigger="props">
      <div class="panel-heading"
           style="cursor: pointer;"
           role="button">

        ## TODO: for some reason buefy will "reuse" the icon
        ## element in such a way that its display does not
        ## refresh.  so to work around that, we use different
        ## structure for the two icons, so buefy is forced to
        ## re-draw

        <b-icon v-if="props.open"
                pack="fas"
                icon="angle-down" />

        <span v-if="!props.open">
          <b-icon pack="fas"
                  icon="angle-right" />
        </span>

        <strong>Installed Packages</strong>
      </div>
    </template>

    <div class="panel-block">
      <div style="width: 100%;">
        ${grid.render_vue_tag(ref='packagesGrid')}
      </div>
    </div>
  </${b}-collapse>

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.configFiles = ${json.dumps([dict(path=p, priority=i) for i, p in enumerate(config.get_prioritized_files(), 1)])|n}

    ThisPage.methods.openInstalledPackages = function() {
        this.$refs.packagesGrid.fetchFirstData()
    }

  </script>
</%def>


${parent.body()}
