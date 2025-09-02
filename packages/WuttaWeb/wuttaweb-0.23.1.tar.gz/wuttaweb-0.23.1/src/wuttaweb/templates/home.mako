## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">Home</%def>

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
    <h1 class="is-size-1">Welcome to ${app.get_title()}</h1>
  </div>
</%def>
