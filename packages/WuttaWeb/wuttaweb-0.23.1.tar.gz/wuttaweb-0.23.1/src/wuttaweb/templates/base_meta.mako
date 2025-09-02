## -*- coding: utf-8; -*-

<%def name="global_title()">${app.get_node_title()}</%def>

<%def name="extra_styles()"></%def>

<%def name="favicon()">
  <link rel="icon" type="image/x-icon" href="${web.get_favicon_url(request)}" />
</%def>

<%def name="header_logo()">
  ${h.image(web.get_header_logo_url(request), "Header Logo", style="height: 49px;")}
</%def>

<%def name="full_logo(image_url=None)">
  ${h.image(image_url or web.get_main_logo_url(request), f"App Logo for {app.get_title()}")}
</%def>

<%def name="footer()">
  <p class="has-text-centered">
    powered by ${h.link_to("WuttaWeb", 'https://wuttaproject.org/', target='_blank')}
  </p>
</%def>
