
Template Lookup
===============

The discovery of templates is handled by Mako, and is configurable.

WuttaWeb comes with all templates it needs, in the path designated as
``wuttaweb:templates``.

When the app renders a page, it invokes the Mako lookup logic, which
searches one or more folders and returns the first matching file it
encounters.  By default ``wuttaweb:templates`` is the only place it
looks.

A template is searched for by "name" but it is more path-like, e.g.
``/page.mako`` or ``/master/index.mako`` etc.  So for example the file
at ``wuttaweb:templates/home.mako`` is used for home page (using
lookup name ``/home.mako``) by default.


.. _mako-template-override:

Overriding the Search Paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The basic idea is to give it a list of paths it should search when
trying to find a template.  The first template file found for a given
search name is used and no further search is done for that name.

You can define the Mako lookup sequence in your ``web.conf`` as
follows:

.. code-block:: ini

   [app:main]
   mako.directories =
       /random/path/on/disk
       poser.web:templates
       wuttaweb:templates

This setting is interpreted by ``pyramid_mako`` (`docs`_).

.. _docs: https://docs.pylonsproject.org/projects/pyramid_mako/en/latest/index.html#mako-directories

Here ``wuttaweb:templates/home.mako`` would still be used by default
for home page, *unless* e.g. ``/random/path/on/disk/home.mako``
existed in which case that would be used.

Each path can have an arbitrary set of templates, they will
effectively be combined to a single set by the app, with the
definition order determining search priority.

If you are already using a custom ``app.main()`` function for
constructing the web app during startup, it may be a good idea to
change the *default* search paths to include your package.

Setup for custom ``app.main()`` is beyond the scope here, but assuming
you *do* already have one, this is what it looks like::

   from wuttaweb import app as base

   def main(global_config, **settings):

       # nb. set the *default* mako search paths; however config can
       # still override with method shown above
       settings.setdefault('mako.directories', ['poser.web:templates',
                                                'wuttaweb:templates'])

       return base.main(global_config, **settings)
