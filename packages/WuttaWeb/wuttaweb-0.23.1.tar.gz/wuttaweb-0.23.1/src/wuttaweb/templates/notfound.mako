## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Not Found</%def>

<%def name="page_content()">
  <div style="padding: 4rem;">
    <p class="block is-size-5">
      Not saying <span class="has-text-weight-bold">you</span> don't
      know what you're talking about..
    </p>
    <p class="block is-size-5">
      ..but <span class="has-text-weight-bold">*I*</span> don't know
      what you're talking about.
    </p>
    <b-field label="Current URL">
      ${request.url}
    </b-field>
  </div>
</%def>


${parent.body()}
