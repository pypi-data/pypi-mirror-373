
Overview
========

WuttaWeb uses the `Mako`_ template language for page rendering.

.. _Mako: https://www.makotemplates.org/

There is a "global" base template which effectively defines the
"theme" (page layout, Vue component structure).  A few other base
templates provide a starting point for any custom pages; see
:doc:`base`.

Templates are found via lookup which is handled by Mako.  This is
configurable so you can override any or all; see :doc:`lookup`.
