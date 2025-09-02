
===================
 Built-in Commands
===================

Below are the :term:`subcommands <subcommand>` which come with
WuttaWeb.


.. _wutta-webapp:

``wutta webapp``
----------------

Run the web app, according to config file(s).

This command is a convenience only; under the hood it can run `uvicorn
<https://www.uvicorn.org/#uvicornrun>`_ but by default will run
whatever :ref:`pserve <pyramid:pserve_script>` is setup to do (which
usually is `waitress
<https://docs.pylonsproject.org/projects/waitress/en/latest/index.html>`_).

Ultimately it's all up to config, so run different web apps with
different config files.

Defined in: :mod:`wuttaweb.cli.webapp`

.. program-output:: wutta webapp --help
