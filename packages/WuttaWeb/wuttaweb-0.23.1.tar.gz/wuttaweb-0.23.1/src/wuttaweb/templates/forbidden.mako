## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Access Denied</%def>

<%def name="page_content()">
  <div style="padding: 4rem;">
    <p class="block is-size-5">
      You are trying to access something for which you do not have permission.
    </p>
    <p class="block is-size-5">
      If you feel this is an error, please ask a site admin to give you access.
    </p>
    % if not request.user:
        <p class="block is-size-5">
          Or probably, you should just ${h.link_to("Login", url('login'))}.
        </p>
    % endif
    <b-field label="Current URL">
      ${request.url}
    </b-field>
  </div>
</%def>


${parent.body()}
