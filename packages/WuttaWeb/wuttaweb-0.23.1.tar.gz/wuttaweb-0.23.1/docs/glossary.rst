.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   grid
     This refers to a "table of data, with features" essentially.
     Sometimes it may be displayed as a simple table with no features,
     or sometimes it has sortable columns, search filters and other
     tools.

     See also the :class:`~wuttaweb.grids.base.Grid` base class.

   menu handler
     This is the :term:`handler` responsible for constructing the main
     app menu at top of page.

     The menu handler is accessed by way of the :term:`web handler`.

     See also the :class:`~wuttaweb.menus.MenuHandler` base class.

   web handler
     This is the :term:`handler` responsible for overall web layer
     customizations, e.g. logo image and menu overrides.  Although
     the latter it delegates to the :term:`menu handler`.

     See also the :class:`~wuttaweb.handler.WebHandler` base class.
