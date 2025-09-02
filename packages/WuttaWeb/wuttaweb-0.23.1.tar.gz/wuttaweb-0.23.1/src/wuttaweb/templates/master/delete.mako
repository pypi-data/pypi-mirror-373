## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="title()">${index_title} &raquo; ${instance_title} &raquo; Delete</%def>

<%def name="content_title()">Delete: ${instance_title}</%def>

<%def name="page_content()">
  <br />
  <b-notification type="is-danger" :closable="false"
                  style="width: 50%;">
    Really DELETE this ${model_title}?
  </b-notification>
  ${parent.page_content()}
</%def>


${parent.body()}
