
Base Templates
==============

This describes the base templates.  When creating a custom page
template, you most often need to inherit from one of these:

* :ref:`page_base_template`
* :ref:`form_base_template`
* :ref:`master_base_templates`

.. note::

   Any of these templates may be overridden; see
   :ref:`mako-template-override`.


Global Base
~~~~~~~~~~~

There is exactly one "true base template" for the web app, designated
as: ``/base.mako``

The default base template is ``wuttaweb:templates/base.mako`` and all
page templates inherit from it.  However they inherit it by *name*
only (``/base.mako``) - therefore if you override this via custom
template search paths, effectively you have changed the **theme**.

In addition to general layout/structure, this template is reponsible
for creating the Vue app which encompasses the whole of every page.
It also establishes the ``WholePage`` component which is the Vue app's
one and only child component.

(``WholePage`` in turn will have other children, for page content.)

There is usually no need to define a template which inherits directly
from ``/base.mako``, rather you should inherit from ``/page.mako``
(see next section) or similar.

As pertains to Vue component logic, there are 3 blocks which you may
find a need to override.  These are defined by ``/base.mako`` so will
apply to *all* templates:

* ``render_vue_templates()``
* ``modify_vue_vars()``
* ``make_vue_components()``

Most often it is necessary to customize ``modify_vue_vars()`` but keep
reading for an example.


.. _page_base_template:

Page Base
~~~~~~~~~

The common base template for pages, designated as: ``/page.mako``

This extends the Vue logic from ``/base.mako`` by establishing
``ThisPage`` component, which wraps all content within the current
page.

The final structure then is conceptually like:

.. code-block:: html

   <div id="app">
     <whole-page>
       <!-- menu etc. -->
       <this-page>
         <!-- page contents -->
       </this-page>
     </whole-page>
   </div>

Simple usage is to create a template which inherits from
``/page.mako`` and defines a ``page_content()`` block, e.g.:

.. code-block:: mako

   <%inherit file="/page.mako" />

   <%def name="page_content()">
     <p>hello world!</p>
   </%def>

The default ``/page.mako`` logic knows where to render the
``page_content()`` block so that it fits properly into the
component/layout structure.

Often you may need to customize Vue component logic for a page; this
is done by defining one of the blocks mentioned in previous section.

Here is a simple example which shows how this works:

.. code-block:: mako

   <%inherit file="/page.mako" />

   <%def name="page_content()">
     <b-field label="Foo">
       <b-input v-model="foo" />
     </b-field>
     <b-field>
     <b-button @click="alertFoo()">
       Alert
     </b-button>
     </b-field>
   </%def>

   <%def name="modify_vue_vars()">
     ${parent.modify_vue_vars()}
     <script>

       // nb. this becomes ThisPage.data.foo
       ThisPageData.foo = 'bar'

       ThisPage.methods.alertFoo = function() {
           alert("value of foo is: " + this.foo)
       }

     </script>
   </%def>

You can see that ``page_content()`` is able to reference things from
``ThisPage`` component, while the ``modify_vue_vars()`` block is used
to define those same things on the component.


.. _form_base_template:

Form Base
~~~~~~~~~

The common base template for pages with a form, designated as:
``/form.mako``

This expects the context dict to contain ``'form'`` which points to a
:class:`~wuttaweb.forms.base.Form` instance.

This template extends the Vue logic from ``/page.mako`` by
establishing a Vue component specific to the form object.

The final structure then is conceptually like:

.. code-block:: html

   <div id="app">
     <whole-page>
       <!-- menu etc. -->
       <this-page>
         <wutta-form>
           <!-- fields etc. -->
         </wutta-form>
       </this-page>
     </whole-page>
   </div>

A simple example which assumes one of the form fields exposes a button
with click event that triggers ``alertFoo()`` method on the form
component:

.. code-block:: mako

   <%inherit file="/form.mako" />

   <%def name="modify_vue_vars()">
     ${parent.modify_vue_vars()}
     <script>

       // nb. this becomes e.g. WuttaForm.foo when component is created
       ${form.vue_component}Data.foo = 'bar'

       ${form.vue_component}.methods.alertFoo = function() {
           alert("value of foo is: " + this.foo)
       }

     </script>
   </%def>

.. note::

   By default, ``${form.vue_compoment}`` is rendered as ``WuttaForm``
   but that is not guaranteed.  You should resist the temptation to
   hard-code that; always use ``${form.vue_component}`` and (where
   applicable) ``${form.vue_tagname}``.

   The reason for this is to allow multiple forms to exist on a single
   page, each with a separate Vue component.  (Which is not shown in
   the above example.)

   See also :attr:`~wuttaweb.forms.base.Form.vue_component` and
   :attr:`~wuttaweb.forms.base.Form.vue_tagname`.


.. _master_base_templates:

Master Base
~~~~~~~~~~~

These templates are for use with
:class:`~wuttaweb.views.master.MasterView`.  Each is the default
template used for the corresponding route/view, unless a more specific
template is defined.

The "index" template is unique in that it is (usually) for listing the
model data:

* ``/master/index.mako``

The "form" template is just a base template, does not directly
correspond to a route/view.  Other CRUD templates inherit from it.
This inherits from ``/form.mako`` (see previous section).

* ``/master/form.mako``

These CRUD templates inherit from ``/master/form.mako`` and so
require a ``'form'`` in the context dict.

* ``/master/create.mako``
* ``/master/view.mako``
* ``/master/edit.mako``
* ``/master/delete.mako``

The "configure" template is for master views which have a
configuration page.

* ``/master/configure.mako``

Usage for these is not significantly different from the ones shown
above, in cases where you actually need to override the template.

As an example let's say you have defined a ``WidgetMasterView`` class
and want to override its "view" template.  You would then create a
file as ``/widgets/view.mako`` (within your templates folder) and
be sure to inherit from the correct base template:

.. code-block:: mako

   <%inherit file="/master/view.mako" />

   <%def name="page_content()">

     <p>THIS APPEARS FIRST!</p>

     ## nb. the form will appear here
     ${parent.page_content()}

     <p>MADE IT TO THE END!</p>

   </%def>
