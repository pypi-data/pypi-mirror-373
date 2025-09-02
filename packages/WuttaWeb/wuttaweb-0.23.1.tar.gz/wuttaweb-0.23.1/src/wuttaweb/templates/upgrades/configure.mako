## -*- coding: utf-8; -*-
<%inherit file="/master/configure.mako" />

<%def name="form_content()">

  <h3 class="is-size-3">Basics</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field label="Upgrade Script (for Execute)"
             message="The command + args will be interpreted by the shell.">
      <b-input name="${app.appname}.upgrades.command"
               v-model="simpleSettings['${app.appname}.upgrades.command']"
               @input="settingsNeedSaved = true"
               ## ref="upgradeSystemCommand"
               ## expanded
               />
    </b-field>

  </div>
</%def>
