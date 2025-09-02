## -*- coding: utf-8 -*-
<html>
  <head>
    <style type="text/css">
      label {
          display: block;
          font-weight: bold;
          margin-top: 1em;
      }
      p {
          margin: 1em 0 1em 1.5em;
      }
      p.msg {
          white-space: pre-wrap;
      }
    </style>
  </head>
  <body>
    <h1>User feedback from website</h1>

    <label>User Name</label>
    <p>
      % if user:
          <a href="${user_url}">${user}</a>
      % else:
          ${user_name}
      % endif
    </p>

    <label>Referring URL</label>
    <p><a href="${referrer}">${referrer}</a></p>

    <label>Client IP</label>
    <p>${client_ip}</p>

    <label>Message</label>
    <p class="msg">${message}</p>

  </body>
</html>
