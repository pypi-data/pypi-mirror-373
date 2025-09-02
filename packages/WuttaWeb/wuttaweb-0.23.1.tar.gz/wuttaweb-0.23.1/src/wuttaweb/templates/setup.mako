## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">First-Time Setup</%def>

<%def name="page_content()">
  <b-notification type="is-success">
    <p class="block">
      The app is running okay!
    </p>
    <p class="block">
      Please setup the first Administrator account below.
    </p>
  </b-notification>

  ${parent.page_content()}
</%def>


${parent.body()}
