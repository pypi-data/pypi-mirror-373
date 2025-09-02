
# Changelog
All notable changes to wuttaweb will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.23.1 (2025-09-01)

### Fix

- fix 'duplicate-code' for pylint
- fix 'no-member' for pylint
- fix 'attribute-defined-outside-init' for pylint
- fix 'arguments-renamed' for pylint
- fix 'arguments-differ' for pylint
- fix 'keyword-arg-before-vararg' for  pylint
- fix 'too-many-nested-blocks' for pylint
- fix 'too-many-locals' for pylint
- fix 'consider-using-generator' for  pylint
- fix 'missing-function-docstring' and 'missing-module-docstring' for pylint
- fix 'super-init-not-called' for pylint
- fix 'singleton-comparison' for pylint
- fix 'simplifiable-if-expression' for pylint
- fix 'redefined-outer-name' for pylint
- fix 'protected-access' for pylint
- fix 'not-callable' for pylint
- fix 'no-else-raise' for pylint
- fix 'isinstance-second-argument-not-valid-type' for pylint
- fix 'consider-using-set-comprehension' for pylint
- fix 'consider-using-get' for pylint
- fix 'consider-using-dict-items' for pylint
- fix 'consider-using-dict-comprehension' for pylint
- fix 'assignment-from-no-return' for pylint
- fix 'abstract-method' for pylint
- fix 'too-few-public-methods' for pylint
- fix 'too-many-lines' for pylint
- fix 'too-many-arguments' for pylint
- fix 'too-many-public-methods' for pylint
- fix 'too-many-statements' for pylint
- fix 'unidiomatic-typecheck' for pylint
- fix 'unnecessary-comprehension' for pylint
- fix 'unnecessary-lambda' and 'unnecessary-lambda-assignment' for pylint
- fix 'unspecified-encoding' for pylint
- fix 'unused-argument' for pylint
- fix 'use-a-generator' for pylint
- fix 'use-dict-literal' for pylint
- fix 'dangerous-default-value' for pylint
- fix 'wildcard-import' and 'unused-wildcard-import' for pylint
- fix 'wrong-import-order' for pylint
- fix 'import-outside-toplevel' for pylint
- fix 'implicit-str-concat' for pylint
- fix 'deprecated-method' for pylint
- fix 'cyclic-import' for pylint
- fix 'bare-except' and 'broad-exception-caught' for pylint
- fix 'invalid-name' for pylint
- fix 'anomalous-backslash-in-string' for pylint
- bump version requirement for wuttjamaican
- fix 'unused-variable' for pylint
- fix 'unused-import' for pylint
- fix 'redefined-argument-from-local' for pylint
- fix 'empty-docstring' for pylint
- fix 'no-else-return' for pylint
- fix 'too-many-branches' for pylint
- fix 'too-many-return-statements' for pylint
- fix 'too-many-instance-attributes' for pylint
- fix 'inconsistent-return-statements' for pylint
- format all code with black

## v0.23.0 (2025-08-09)

### Feat

- add tools to manage user API tokens

### Fix

- add default sorter, tools for basic table-element grid
- add custom password+confirmation widget for Vue3 + Oruga
- fix butterfly wrapper for b-notification component
- add butterfly wrapper for b-timepicker component
- style tweaks for butterfly/oruga; mostly expand fields
- fix b-datepicker component wrapper per oruga 0.9.0
- fix b-button component wrapper per oruga 0.9.0
- update butterfly component for b-autocomplete, per oruga 0.11.4
- update default versions for Vue3 + Oruga + FontAwesome

## v0.22.0 (2025-06-29)

### Feat

- add basic theme system

### Fix

- improve styles for testing watermark background image
- fix timezone offset bug for datepicker

## v0.21.5 (2025-02-21)

### Fix

- avoid newer `EnumType` for python <= 3.10

## v0.21.4 (2025-02-21)

### Fix

- add value choice/enum support for grid filters

## v0.21.3 (2025-02-19)

### Fix

- add click handler support in simple grid table element
- hide columns when applicable, for simple grid table element
- add `render_form_tag()` customization hook in /form template

## v0.21.2 (2025-02-18)

### Fix

- add hidden flag for grid columns

## v0.21.1 (2025-02-17)

### Fix

- fix warning msg for deprecated setting

## v0.21.0 (2025-02-01)

### Feat

- overhaul some User/Person form fields etc.

### Fix

- do not auto-create grid filters for uuid columns

## v0.20.6 (2025-01-26)

### Fix

- add `setup_enhance_admin_user()` method for initial setup
- add `render_percent()` method for Grid
- allow override for Admin menu title
- add `index_title_controls()` def block for base template
- add `make_users_grid()` method for RoleView
- fallback to empty string for uvicorn `root_path`
- add `root_path` config setting for running webapp via uvicorn

## v0.20.5 (2025-01-23)

### Fix

- improve styling for grid tools section
- add basic checkbox support for grids
- add WuttaRequestMixin for ThisPage component
- avoid literal `None` when rendering form field value
- let header title be even wider

## v0.20.4 (2025-01-15)

### Fix

- add `WuttaDateWidget` and associated logic
- add  `serialize_object()` method for `ObjectRef` schema node

## v0.20.3 (2025-01-14)

### Fix

- add `render_grid_tag()` as separate def block for index templates
- add `click_handler` attr for GridAction

## v0.20.2 (2025-01-14)

### Fix

- improve support for composite `model_key` in MasterView
- let content header text be a bit longer
- add optional `target` attr for GridAction
- add `render_date()` method for grids

## v0.20.1 (2025-01-13)

### Fix

- expose setting to choose menu handler, in appinfo/configure
- use prop key instead of column name, for master view model key
- add grid filters specific to numeric, integer types
- use default value for config settings

## v0.20.0 (2025-01-11)

### Feat

- add basic views for Reports

### Fix

- add `action_method` and `reset_url` params for Form class
- add placeholder when grid has no filters
- add `get_page_templates()` method for master view

## v0.19.3 (2025-01-09)

### Fix

- use `request.url` instead of `current_route_url()`
- add basic `<wutta-autocomplete>` component
- add `WuttaDictEnum` form schema type

## v0.19.2 (2025-01-07)

### Fix

- always use prop key for default grid filters
- avoid `request.current_route_url()` for user menu
- add `scale` kwarg for `WuttaMoney` schema type, widget
- make WuttaQuantity serialize w/ app handler, remove custom widget
- bugfix for bool simple settings with default value

## v0.19.1 (2025-01-06)

### Fix

- improve built-in grid renderer logic
- allow session injection for ObjectRef constructor
- improve rendering for batch row status
- add basic support for row grid "view" action links
- add "xref buttons" tool panel for master view
- add WuttaQuantity schema type, widget
- remove `session` param from some form schema, widget classes
- add grid renderers for bool, currency, quantity
- use proper bulma styles for markdown content
- use span element for readonly money field widget render
- include grid filters for all column properties of model class
- use app handler to render error string, when progress fails
- add schema node type, widget for "money" (currency) fields
- exclude FK fields by default, for model forms
- fix style for header title text

## v0.19.0 (2024-12-23)

### Feat

- add feature to edit email settings, basic message preview

### Fix

- move CRUD header buttons toward center of screen

## v0.18.0 (2024-12-18)

### Feat

- add basic support for running in ASGI context
- add support for running via uvicorn; `wutta webapp` command

## v0.17.2 (2024-12-17)

### Fix

- add basic support for grid filters for Date fields
- fix style bug for grid "add filter" autocomplete

## v0.17.1 (2024-12-16)

### Fix

- tweak wording for batch execution
- let view subclass more easily inject kwargs for `make_batch()`

## v0.17.0 (2024-12-15)

### Feat

- add basic support for batch execution
- add basic support for rows grid for master, batch views
- add basic master view class for batches

### Fix

- add handling for decimal values and lists, in `make_json_safe()`
- fix behavior when editing Roles for a User
- add basic views for raw Permissions
- improve support for date, datetime fields in grids, forms
- add way to set field widgets using pseudo-type
- add support for date, datetime form fields
- make dropdown widgets as wide as other text fields in main form
- add fallback instance title
- display "global" errors at top of form, if present
- add `make_form()` and `make_grid()` methods on web handler
- correct "empty option" behavior for `ObjectRef` schema type
- use fanstatic to serve built-in images by default

## v0.16.2 (2024-12-10)

### Fix

- add `GridWidget` and `form.set_grid()` for convenience
- add "is false or null" grid filter, for nullable bool columns
- remove Person column for `Person.users` grid display
- flatten UUID to str for `make_json_safe()`

## v0.16.1 (2024-12-08)

### Fix

- refactor to reflect usage of proper UUID values

## v0.16.0 (2024-12-05)

### Feat

- add `get_template_context()` method for master view

### Fix

- add option for People entry in the Admin menu
- fix handling of `Upgrade.uuid`
- improve support for random objects with grid, master view
- hide CRUD header buttons if master view does not allow

## v0.15.0 (2024-11-24)

### Feat

- add logic to prevent edit for some user accounts

### Fix

- fix default form value logic for bool checkbox fields
- always use configured app dist for appinfo/index page

## v0.14.2 (2024-11-24)

### Fix

- remove 'email' extra from wuttjamaican dependency
- omit `id` attr when rendering hidden input for CSRF token

## v0.14.1 (2024-08-30)

### Fix

- avoid exit prompt for configure when removing settings
- freeze default versions for buefy, vue-resource
- stop auto-trim for feedback message, user name

## v0.14.0 (2024-08-27)

### Feat

- add basic support for wutta-continuum

## v0.13.1 (2024-08-26)

### Fix

- allow custom base template to add params to feedback form

## v0.13.0 (2024-08-26)

### Feat

- use native wuttjamaican app to send feedback email
- add basic user feedback email mechanism
- add "progress" page for executing upgrades
- add basic support for execute upgrades, download stdout/stderr
- add basic progress page/indicator support
- add basic "delete results" grid tool
- add initial views for upgrades
- allow app db to be rattail-native instead of wutta-native
- add per-row css class support for grids
- improve grid filter API a bit, support string/bool filters

### Fix

- tweak max image size for full logo on home, login pages
- improve handling of boolean form fields
- misc. improvements for display of grids, form errors
- use autocomplete for grid filter verb choices
- small cleanup for grid filters template
- add once-button action for grid Reset View
- set sort defaults for users, roles
- add override hook for base form template

## v0.12.1 (2024-08-22)

### Fix

- improve home, login page styles for large logo image

## v0.12.0 (2024-08-22)

### Feat

- add "copy link" button for sharing a grid view
- add initial support for proper grid filters
- add initial filtering logic to grid class
- add "searchable" column support for grids
- improve page linkage between role/user/person
- add basic autocomplete support, for Person

### Fix

- cleanup templates for home, login pages
- cleanup logic for appinfo/configure
- expose settings for app node title, type
- show installed python packages on appinfo page
- tweak login form to stop extending size of background card
- add setting to auto-redirect anon users to login, from home page
- add form padding, validators for /configure pages
- add padding around main form, via wrapper css
- show CRUD buttons in header only if relevant and user has access
- tweak style config for home link app title in main menu

## v0.11.0 (2024-08-20)

### Feat

- split up base templates into more sections (def blocks)
- simplify base/page/form template structure; add docs

## v0.10.2 (2024-08-19)

### Fix

- add `render_vue_finalize()` methods for grids, forms
- avoid error when checking model for column property

## v0.10.1 (2024-08-19)

### Fix

- make `util.get_model_fields()` work with more model classes

## v0.10.0 (2024-08-18)

### Feat

- add multi-column sorting (frontend or backend) for grids

### Fix

- improve grid display when data is empty

## v0.9.0 (2024-08-16)

### Feat

- add backend pagination support for grids
- add initial/basic pagination for grids

## v0.8.1 (2024-08-15)

### Fix

- improve backward compat for `util.get_liburl()`

## v0.8.0 (2024-08-15)

### Feat

- add form/grid label auto-overrides for master view

### Fix

- add `person` to template context for `PersonView.view_profile()`

## v0.7.0 (2024-08-15)

### Feat

- add sane views for 403 Forbidden and 404 Not Found
- add permission checks for menus, view routes
- add first-time setup page to create admin user
- expose User password for editing in master views
- expose Role permissions for editing
- expose User "roles" for editing
- improve widget, rendering for Role notes

### Fix

- add stub for `PersonView.make_user()`
- allow arbitrary kwargs for `Form.render_vue_field()`
- make some tweaks for better tailbone compatibility
- prevent delete for built-in roles

## v0.6.0 (2024-08-13)

### Feat

- add basic Roles view
- add Users view; improve CRUD master for SQLAlchemy models
- add People view; improve CRUD master for SQLAlchemy models
- add basic support for SQLAlchemy model in master view
- add basic Create support for CRUD master view
- add basic Delete support for CRUD master view
- add basic Edit support for CRUD master view
- add auto-link (to "View") behavior for grid columns
- add basic support for "view" part of CRUD
- add basic `Grid` class, and /settings master view

### Fix

- rename MasterView method to `configure_grid()`
- replace default logo, favicon images
- tweak labels for Web Libraries config

## v0.5.0 (2024-08-06)

### Feat

- add basic support for fanstatic / libcache
- expose Web Libraries in app info config page
- add basic configure view for appinfo

### Fix

- bump min version for wuttjamaican

## v0.4.0 (2024-08-05)

### Feat

- add basic App Info view (index only)
- add initial `MasterView` support

### Fix

- add `notfound()` View method; auto-append trailing slash
- bump min version for wuttjamaican

## v0.3.0 (2024-08-05)

### Feat

- add support for admin user to become / stop being root
- add view to change current user password
- add basic logo, favicon images
- add auth views, for login/logout
- add custom security policy, login/logout for pyramid
- add `wuttaweb.views.essential` module
- add initial/basic forms support
- add `wuttaweb.db` module, with `Session`
- add `util.get_form_data()` convenience function

### Fix

- allow custom user getter for `new_request_set_user()` hook

## v0.2.0 (2024-07-14)

### Feat

- add basic support for menu handler

- add "web handler" feature; it must get the menu handler

## v0.1.0 (2024-07-12)

### Feat

- basic support for WSGI app, views, templates
