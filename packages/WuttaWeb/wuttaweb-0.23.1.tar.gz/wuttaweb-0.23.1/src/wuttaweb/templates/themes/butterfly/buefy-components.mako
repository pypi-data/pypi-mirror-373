
<%def name="make_buefy_components()">
  ${self.make_b_autocomplete_component()}
  ${self.make_b_button_component()}
  ${self.make_b_checkbox_component()}
  ${self.make_b_collapse_component()}
  ${self.make_b_datepicker_component()}
  ${self.make_b_timepicker_component()}
  ${self.make_b_dropdown_component()}
  ${self.make_b_dropdown_item_component()}
  ${self.make_b_field_component()}
  ${self.make_b_icon_component()}
  ${self.make_b_input_component()}
  ${self.make_b_loading_component()}
  ${self.make_b_modal_component()}
  ${self.make_b_notification_component()}
  ${self.make_b_radio_component()}
  ${self.make_b_select_component()}
  ${self.make_b_steps_component()}
  ${self.make_b_step_item_component()}
  ${self.make_b_table_component()}
  ${self.make_b_table_column_component()}
  ${self.make_b_tooltip_component()}
  ${self.make_once_button_component()}
</%def>

<%def name="make_b_autocomplete_component()">
  <script type="text/x-template" id="b-autocomplete-template">
    <o-autocomplete v-model:input="orugaValue"
                    :options="options"
                    clear-icon="circle-xmark"
                    @update:input="orugaValueUpdated"
                    ref="autocomplete">
    </o-autocomplete>
  </script>
  <script>
    const BAutocomplete = {
        template: '#b-autocomplete-template',
        props: {
            modelValue: String,
            data: Array,
            field: String,
            customFormatter: null,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                if (this.orugaValue != to) {
                    this.orugaValue = to
                }
            },
        },
        computed: {
            options() {
                const options = []
                const field = this.field || 'label'
                for (let opt of this.data) {
                    const newOpt = {
                        label: opt[field],
                        value: opt,
                    }
                    if (this.customFormatter) {
                        newOpt.label = this.customFormatter(opt)
                    }
                    options.push(newOpt)
                }
                return options
            },
        },
        methods: {
            focus() {
                const input = this.$refs.autocomplete.$el.querySelector('input')
                input.focus()
            },
            orugaValueUpdated(value) {
                if (this.field) {
                    value = value[this.field]
                }
                this.$emit('update:modelValue', value || '')
            },
        },
    }
  </script>
  <% request.register_component('b-autocomplete', 'BAutocomplete') %>
</%def>

<%def name="make_b_button_component()">
  <script type="text/x-template" id="b-button-template">
    <o-button :variant="variant"
              :size="orugaSize"
              :type="nativeType"
              :tag="tag"
              :href="href"
              :icon-left="iconLeft">
      <slot />
    </o-button>
  </script>
  <script>
    const BButton = {
        template: '#b-button-template',
        props: {
            type: String,
            nativeType: String,
            tag: String,
            href: String,
            size: String,
            iconPack: String, // ignored
            iconLeft: String,
        },
        computed: {
            orugaSize() {
                if (this.size) {
                    return this.size.replace(/^is-/, '')
                }
            },
            variant() {
                if (this.type) {
                    return this.type.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-button', 'BButton') %>
</%def>

<%def name="make_b_checkbox_component()">
  <script type="text/x-template" id="b-checkbox-template">
    <o-checkbox v-model="orugaValue"
                @update:model-value="orugaValueUpdated"
                :name="name"
                :native-value="nativeValue">
      <slot />
    </o-checkbox>
  </script>
  <script>
    const BCheckbox = {
        template: '#b-checkbox-template',
        props: {
            modelValue: null,
            name: String,
            nativeValue: null,
            value: null,
        },
        data() {
            return {
                orugaValue: this.modelValue || this.value,
            }
        },
        watch: {
            modelValue(to, from) {
                this.orugaValue = to
            },
        },
        methods: {
            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
            },
        },
    }
  </script>
  <% request.register_component('b-checkbox', 'BCheckbox') %>
</%def>

<%def name="make_b_collapse_component()">
  <script type="text/x-template" id="b-collapse-template">
    <o-collapse :open="open">
      <slot name="trigger" />
      <slot />
    </o-collapse>
  </script>
  <script>
    const BCollapse = {
        template: '#b-collapse-template',
        props: {
            open: Boolean,
        },
    }
  </script>
  <% request.register_component('b-collapse', 'BCollapse') %>
</%def>

<%def name="make_b_datepicker_component()">
  <script type="text/x-template" id="b-datepicker-template">
    <o-datepicker :name="name"
                  v-model="orugaValue"
                  @update:model-value="orugaValueUpdated"
                  :value="value"
                  :placeholder="placeholder"
                  :formatter="dateFormatter"
                  :parser="dateParser"
                  :disabled="disabled"
                  :editable="editable"
                  :icon="icon"
                  :close-on-click="false">
    </o-datepicker>
  </script>
  <script>
    const BDatepicker = {
        template: '#b-datepicker-template',
        props: {
            dateFormatter: null,
            dateParser: null,
            disabled: Boolean,
            editable: Boolean,
            icon: String,
            // iconPack: String,   // ignored
            modelValue: Date,
            name: String,
            placeholder: String,
            value: null,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                if (this.orugaValue != to) {
                    this.orugaValue = to
                }
            },
        },
        methods: {
            orugaValueUpdated(value) {
                if (this.modelValue != value) {
                    this.$emit('update:modelValue', value)
                }
            },
        },
    }
  </script>
  <% request.register_component('b-datepicker', 'BDatepicker') %>
</%def>

<%def name="make_b_timepicker_component()">
  <script type="text/x-template" id="b-timepicker-template">
    <o-timepicker v-model="orugaValue"
                  @update:model-value="orugaValueUpdated"
                  :formatter="timeFormatter"
                  :parser="timeParser" />
  </script>
  <script>
    const BTimepicker = {
        template: '#b-timepicker-template',
        props: {
            modelValue: null,
            timeFormatter: null,
            timeParser: null,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                if (this.orugaValue != to) {
                    this.orugaValue = to
                }
            },
        },
        methods: {
            orugaValueUpdate(value) {
                if (this.modelValue != value) {
                    this.$emit('update:modelValue', value)
                }
            },
        },
    }
  </script>
  <% request.register_component('b-timepicker', 'BTimepicker') %>
</%def>

<%def name="make_b_dropdown_component()">
  <script type="text/x-template" id="b-dropdown-template">
    <o-dropdown :position="buefyPosition"
                :triggers="triggers">
      <slot name="trigger" />
      <slot />
    </o-dropdown>
  </script>
  <script>
    const BDropdown = {
        template: '#b-dropdown-template',
        props: {
            position: String,
            triggers: Array,
        },
        computed: {
            buefyPosition() {
                if (this.position) {
                    return this.position.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-dropdown', 'BDropdown') %>
</%def>

<%def name="make_b_dropdown_item_component()">
  <script type="text/x-template" id="b-dropdown-item-template">
    <o-dropdown-item :label="label">
      <slot />
    </o-dropdown-item>
  </script>
  <script>
    const BDropdownItem = {
        template: '#b-dropdown-item-template',
        props: {
            label: String,
        },
    }
  </script>
  <% request.register_component('b-dropdown-item', 'BDropdownItem') %>
</%def>

<%def name="make_b_field_component()">
  <script type="text/x-template" id="b-field-template">
    <o-field :grouped="grouped"
             :label="label"
             :horizontal="horizontal"
             :expanded="expanded"
             :variant="variant">
      <slot />
    </o-field>
  </script>
  <script>
    const BField = {
        template: '#b-field-template',
        props: {
            expanded: Boolean,
            grouped: Boolean,
            horizontal: Boolean,
            label: String,
            type: String,
        },
        computed: {
            variant() {
                if (this.type) {
                    return this.type.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-field', 'BField') %>
</%def>

<%def name="make_b_icon_component()">
  <script type="text/x-template" id="b-icon-template">
    <o-icon :icon="icon"
            :size="orugaSize" />
  </script>
  <script>
    const BIcon = {
        template: '#b-icon-template',
        props: {
            icon: String,
            size: String,
        },
        computed: {
            orugaSize() {
                if (this.size) {
                    return this.size.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-icon', 'BIcon') %>
</%def>

<%def name="make_b_input_component()">
  <script type="text/x-template" id="b-input-template">
    <o-input :type="type"
             :disabled="disabled"
             v-model="orugaValue"
             @update:modelValue="val => $emit('update:modelValue', val)"
             :autocomplete="autocomplete"
             ref="input"
             :expanded="expanded">
      <slot />
    </o-input>
  </script>
  <script>
    const BInput = {
        template: '#b-input-template',
        props: {
            modelValue: null,
            type: String,
            autocomplete: String,
            disabled: Boolean,
            expanded: Boolean,
        },
        data() {
            return {
                orugaValue: this.modelValue
            }
        },
        watch: {
            modelValue(to, from) {
                if (this.orugaValue != to) {
                    this.orugaValue = to
                }
            },
        },
        methods: {
            focus() {
                this.$refs.input.focus()
            },
        },
    }
  </script>
  <% request.register_component('b-input', 'BInput') %>
</%def>

<%def name="make_b_loading_component()">
  <script type="text/x-template" id="b-loading-template">
    <o-loading :full-page="isFullPage">
      <slot />
    </o-loading>
  </script>
  <script>
    const BLoading = {
        template: '#b-loading-template',
        props: {
            isFullPage: Boolean,
        },
    }
  </script>
  <% request.register_component('b-loading', 'BLoading') %>
</%def>

<%def name="make_b_modal_component()">
  <script type="text/x-template" id="b-modal-template">
    <o-modal v-model:active="trueActive"
             @update:active="activeChanged">
      <slot />
    </o-modal>
  </script>
  <script>
    const BModal = {
        template: '#b-modal-template',
        props: {
            active: Boolean,
            hasModalCard: Boolean, // nb. this is ignored
        },
        data() {
            return {
                trueActive: this.active,
            }
        },
        watch: {
            active(to, from) {
                this.trueActive = to
            },
            trueActive(to, from) {
                if (this.active != to) {
                    this.tellParent(to)
                }
            },
        },
        methods: {

            tellParent(active) {
                // TODO: this does not work properly
                this.$emit('update:active', active)
            },

            activeChanged(active) {
                this.tellParent(active)
            },
        },
    }
  </script>
  <% request.register_component('b-modal', 'BModal') %>
</%def>

<%def name="make_b_notification_component()">
  <script type="text/x-template" id="b-notification-template">
    <o-notification :variant="variant"
                    ## nb. prop name changed for oruga
                    :closeable="closable">
      <slot />
    </o-notification>
  </script>
  <script>
    const BNotification = {
        template: '#b-notification-template',
        props: {
            type: String,
            closable: {
                type: Boolean,
                default: true,
            },
        },
        computed: {
            variant() {
                if (this.type) {
                    return this.type.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-notification', 'BNotification') %>
</%def>

<%def name="make_b_radio_component()">
  <script type="text/x-template" id="b-radio-template">
    <o-radio v-model="orugaValue"
             @update:model-value="orugaValueUpdated"
             :native-value="nativeValue">
      <slot />
    </o-radio>
  </script>
  <script>
    const BRadio = {
        template: '#b-radio-template',
        props: {
            modelValue: null,
            nativeValue: null,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                this.orugaValue = to
            },
        },
        methods: {
            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
            },
        },
    }
  </script>
  <% request.register_component('b-radio', 'BRadio') %>
</%def>

<%def name="make_b_select_component()">
  <script type="text/x-template" id="b-select-template">
    <o-select :name="name"
              ref="select"
              v-model="orugaValue"
              @update:model-value="orugaValueUpdated"
              :expanded="expanded"
              :multiple="multiple"
              :size="orugaSize"
              :native-size="nativeSize">
      <slot />
    </o-select>
  </script>
  <script>
    const BSelect = {
        template: '#b-select-template',
        props: {
            expanded: Boolean,
            modelValue: null,
            multiple: Boolean,
            name: String,
            nativeSize: null,
            size: null,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                this.orugaValue = to
            },
        },
        computed: {
            orugaSize() {
                if (this.size) {
                    return this.size.replace(/^is-/, '')
                }
            },
        },
        methods: {
            focus() {
                this.$refs.select.focus()
            },
            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
                this.$emit('input', value)
            },
        },
    }
  </script>
  <% request.register_component('b-select', 'BSelect') %>
</%def>

<%def name="make_b_steps_component()">
  <script type="text/x-template" id="b-steps-template">
    <o-steps v-model="orugaValue"
             @update:model-value="orugaValueUpdated"
             :animated="animated"
             :rounded="rounded"
             :has-navigation="hasNavigation"
             :vertical="vertical">
      <slot />
    </o-steps>
  </script>
  <script>
    const BSteps = {
        template: '#b-steps-template',
        props: {
            modelValue: null,
            animated: Boolean,
            rounded: Boolean,
            hasNavigation: Boolean,
            vertical: Boolean,
        },
        data() {
            return {
                orugaValue: this.modelValue,
            }
        },
        watch: {
            modelValue(to, from) {
                this.orugaValue = to
            },
        },
        methods: {
            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
                this.$emit('input', value)
            },
        },
    }
  </script>
  <% request.register_component('b-steps', 'BSteps') %>
</%def>

<%def name="make_b_step_item_component()">
  <script type="text/x-template" id="b-step-item-template">
    <o-step-item :step="step"
                 :value="value"
                 :label="label"
                 :clickable="clickable">
      <slot />
    </o-step-item>
  </script>
  <script>
    const BStepItem = {
        template: '#b-step-item-template',
        props: {
            step: null,
            value: null,
            label: String,
            clickable: Boolean,
        },
    }
  </script>
  <% request.register_component('b-step-item', 'BStepItem') %>
</%def>

<%def name="make_b_table_component()">
  <script type="text/x-template" id="b-table-template">
    <o-table :data="data">
      <slot />
    </o-table>
  </script>
  <script>
    const BTable = {
        template: '#b-table-template',
        props: {
            data: Array,
        },
    }
  </script>
  <% request.register_component('b-table', 'BTable') %>
</%def>

<%def name="make_b_table_column_component()">
  <script type="text/x-template" id="b-table-column-template">
    <o-table-column :field="field"
                    :label="label"
                    v-slot="props">
      ## TODO: this does not seem to really work for us...
      <slot :props="props" />
    </o-table-column>
  </script>
  <script>
    const BTableColumn = {
        template: '#b-table-column-template',
        props: {
            field: String,
            label: String,
        },
    }
  </script>
  <% request.register_component('b-table-column', 'BTableColumn') %>
</%def>

<%def name="make_b_tooltip_component()">
  <script type="text/x-template" id="b-tooltip-template">
    <o-tooltip :label="label"
               :position="orugaPosition"
               :multiline="multilined">
      <slot />
    </o-tooltip>
  </script>
  <script>
    const BTooltip = {
        template: '#b-tooltip-template',
        props: {
            label: String,
            multilined: Boolean,
            position: String,
        },
        computed: {
            orugaPosition() {
                if (this.position) {
                    return this.position.replace(/^is-/, '')
                }
            },
        },
    }
  </script>
  <% request.register_component('b-tooltip', 'BTooltip') %>
</%def>

<%def name="make_once_button_component()">
  <script type="text/x-template" id="once-button-template">
    <b-button :type="type"
              :native-type="nativeType"
              :tag="tag"
              :href="href"
              :title="title"
              :disabled="buttonDisabled"
              @click="clicked"
              icon-pack="fas"
              :icon-left="iconLeft">
      {{ buttonText }}
    </b-button>
  </script>
  <script>
    const OnceButton = {
        template: '#once-button-template',
        props: {
            type: String,
            nativeType: String,
            tag: String,
            href: String,
            text: String,
            title: String,
            iconLeft: String,
            working: String,
            workingText: String,
            disabled: Boolean,
        },
        data() {
            return {
                currentText: null,
                currentDisabled: null,
            }
        },
        computed: {
            buttonText: function() {
                return this.currentText || this.text
            },
            buttonDisabled: function() {
                if (this.currentDisabled !== null) {
                    return this.currentDisabled
                }
                return this.disabled
            },
        },
        methods: {

            clicked(event) {
                this.currentDisabled = true
                if (this.workingText) {
                    this.currentText = this.workingText
                } else if (this.working) {
                    this.currentText = this.working + ", please wait..."
                } else {
                    this.currentText = "Working, please wait..."
                }
                // this.$nextTick(function() {
                //     this.$emit('click', event)
                // })
            }
        },
    }
  </script>
  <% request.register_component('once-button', 'OnceButton') %>
</%def>
