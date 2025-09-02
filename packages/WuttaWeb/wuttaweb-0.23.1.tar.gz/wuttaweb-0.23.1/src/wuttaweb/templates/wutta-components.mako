
<%def name="make_wutta_components()">
  ${self.make_wutta_request_mixin()}
  ${self.make_wutta_autocomplete_component()}
  ${self.make_wutta_button_component()}
  ${self.make_wutta_checked_password_component()}
  ${self.make_wutta_datepicker_component()}
  ${self.make_wutta_timepicker_component()}
  ${self.make_wutta_filter_component()}
  ${self.make_wutta_filter_value_component()}
  ${self.make_wutta_filter_date_value_component()}
  ${self.make_wutta_tool_panel_component()}
</%def>

<%def name="make_wutta_request_mixin()">
  <script>

    const WuttaRequestMixin = {
        methods: {

            wuttaGET(url, params, success, failure) {

                this.$http.get(url, {params: params}).then(response => {

                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: `Request failed:  ${'$'}{response.data.error}`,
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        if (failure) {
                            failure(response)
                        }

                    } else {
                        success(response)
                    }

                }, response => {
                    this.$buefy.toast.open({
                        message: "Request failed:  (unknown server error)",
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })

            },

            wuttaPOST(action, params, success, failure) {

                const csrftoken = ${json.dumps(h.get_csrf_token(request))|n}
                const headers = {'X-CSRF-TOKEN': csrftoken}

                this.$http.post(action, params, {headers: headers}).then(response => {

                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: "Submit failed:  " + (response.data.error ||
                                                           "(unknown error)"),
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        if (failure) {
                            failure(response)
                        }

                    } else {
                        success(response)
                    }

                }, response => {
                    this.$buefy.toast.open({
                        message: "Submit failed!  (unknown server error)",
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })
            },
        },
    }

  </script>
</%def>

<%def name="make_wutta_autocomplete_component()">
  <script type="text/x-template" id="wutta-autocomplete-template">
    <div>
      <b-autocomplete ref="autocomplete"
                      v-show="!value"
                      v-model="entry"
                      :data="data"
                      @typing="getAsyncData"
                      @select="selectionMade"
                      keep-first>
        <template slot-scope="props">
          {{ props.option.label }}
        </template>
      </b-autocomplete>
      <b-button v-if="value"
                @click="clearValue(true, true)">
        {{ recordLabel }} (click to change)
      </b-button>
    </div>
  </script>
  <script>
    const WuttaAutocomplete = {
        template: '#wutta-autocomplete-template',

        props: {

            // callers do not specify this directly but rather by way
            // of the `v-model` directive.  the component will emit
            // `input` events when this value changes
            value: String,

            // caller must specify initial display string, if the
            // (v-model) value is not empty when component loads
            display: String,

            // the url from which search results are obtained.  the
            // endpoint should expect a GET with single `term` param
            // in query string, and return list of objects, each with
            // (at least) `value` and `label` properties.
            serviceUrl: String,
        },

        data() {
            return {

                // user search input
                entry: null,

                // display label for button, when value is set
                recordLabel: this.display,

                // this contains the latest search results; it will
                // change over time as user types.  when an option is
                // selected, it will be an element from this list.
                data: [],
            }
        },

        watch: {

            value(val) {
                // reset ourself when model value is cleared
                if (!val) {
                    this.clearValue()
                }
            },
        },

        methods: {

            focus() {
                this.$refs.autocomplete.focus()
            },

            // convenience for parent component to fetch current label
            getLabel() {
                return this.recordLabel
            },

            // fetch new search results from server.  this is invoked
            // when user types new input
            getAsyncData(entry) {

                // nb. skip search until we have at least 3 chars of input
                if (entry.length < 3) {
                    this.data = []
                    return
                }

                // search results become autocomplete options
                this.$http.get(this.serviceUrl + '?term=' + encodeURIComponent(entry))
                    .then(({ data }) => {
                        this.data = data
                    })
                    .catch((error) => {
                        this.data = []
                        throw error
                    })
            },

            // handle selection change.  this is invoked when user
            // chooses an autocomplete option
            selectionMade(option) {

                // reset user input
                this.entry = null

                // nb. this method can be triggered when a selection
                // is made *or cleared* - if the latter then we do not
                // want to emit event for the empty value; that part
                // is handled in clearValue()
                if (option) {
                    this.recordLabel = option.label
                    this.$emit('input', option.value)
                } else {
                    this.recordLabel = null
                }
            },

            // clear the component value
            clearValue(emit, focus) {

                // clear autocomplete selection
                this.$refs.autocomplete.setSelected(null)

                // maybe emit event for new value
                if (emit) {
                    this.$emit('input', null)
                }

                // maybe set focus to autocomplete
                if (focus) {
                    this.$nextTick(function() {
                        this.focus()
                    })
                }
            },
        },

    }
    Vue.component('wutta-autocomplete', WuttaAutocomplete)
    <% request.register_component('wutta-autocomplete', 'WuttaAutocomplete') %>
  </script>
</%def>

<%def name="make_wutta_button_component()">
  <script type="text/x-template" id="wutta-button-template">
    <b-button :type="type"
              :native-type="nativeType"
              :tag="tag"
              :href="href"
              :title="title"
              :disabled="buttonDisabled"
              @click="clicked"
              icon-pack="fas"
              :icon-left="iconLeft">
      {{ buttonLabel }}
    </b-button>
  </script>
  <script>
    const WuttaButton = {
        template: '#wutta-button-template',
        props: {
            type: String,
            nativeType: String,
            tag: String,
            href: String,
            label: String,
            title: String,
            iconLeft: String,
            working: String,
            workingLabel: String,
            disabled: Boolean,
            once: Boolean,
        },
        data() {
            return {
                currentLabel: null,
                currentDisabled: null,
            }
        },
        computed: {
            buttonLabel: function() {
                return this.currentLabel || this.label
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
                if (this.once) {
                    this.currentDisabled = true
                    if (this.workingLabel) {
                        this.currentLabel = this.workingLabel
                    } else if (this.working) {
                        this.currentLabel = this.working + ", please wait..."
                    } else {
                        this.currentLabel = "Working, please wait..."
                    }
                }
            }
        },
    }
    Vue.component('wutta-button', WuttaButton)
    <% request.register_component('wutta-button', 'WuttaButton') %>
  </script>
</%def>

<%def name="make_wutta_checked_password_component()">
  <script type="text/x-template" id="wutta-checked-password-template">
    <div>
      <b-input type="password"
               placeholder="Password"
               v-model="password"
               @input="passwordUpdated"
               expanded />
      <b-input type="password"
               placeholder="Confirm Password"
               v-model="passwordConfirm"
               @input="passwordConfirmUpdated"
               expanded />
      <input type="hidden" :name="name" :value="passwordFinal" />
    </div>
  </script>
  <script>
    const WuttaCheckedPassword = {
        template: '#wutta-checked-password-template',
        props: {
            modelValue: null,
            name: String,
        },
        data() {
            return {
                password: null,
                passwordConfirm: null,
                passwordFinal: null,
            }
        },
        methods: {

            passwordUpdated(val) {
                this.passwordFinal = (val && this.passwordConfirm == val) ? val : null
                this.$emit('update:modelValue', this.passwordFinal)
            },

            passwordConfirmUpdated(val) {
                this.passwordFinal = (val && this.password == val) ? val : null
                this.$emit('update:modelValue', this.passwordFinal)
            },
        },
    }
    Vue.component('wutta-checked-password', WuttaCheckedPassword)
    <% request.register_component('wutta-checked-password', 'WuttaCheckedPassword') %>
  </script>
</%def>

<%def name="make_wutta_datepicker_component()">
  <script type="text/x-template" id="wutta-datepicker-template">
    <b-datepicker :name="name"
                  ref="datepicker"
                  :editable="editable"
                  icon-pack="fas"
                  icon="calendar-alt"
                  :date-formatter="formatDate"
                  :value="buefyValue"
                  :size="size"
                  @input="val => $emit('input', val)" />
  </script>
  <script>
    const WuttaDatepicker = {
        template: '#wutta-datepicker-template',
        props: {
            name: String,
            value: String,
            size: String,
            editable: {
                type: Boolean,
                default: true,
            },
        },
        data() {
            return {
                buefyValue: this.parseDate(this.value),
            }
        },
        methods: {

            focus() {
                this.$refs.datepicker.focus()
            },

            formatDate(date) {
                if (date === null) {
                    return null
                }
                // just need to convert to simple ISO date format here, seems
                // like there should be a more obvious way to do that?
                // nb. also, not sure if/what i am missing here but
                // when user keys in a date, the component must assume
                // UTC (?)  but the value passed to this method may be
                // offset in such a way that a *different date* is
                // implied!  hence we must convert back to UTC when
                // isolating each part.. *shrug*
                var year = date.getUTCFullYear()
                var month = date.getUTCMonth() + 1
                var day = date.getUTCDate()
                month = month < 10 ? '0' + month : month
                day = day < 10 ? '0' + day : day
                return year + '-' + month + '-' + day
            },

            parseDate(date) {
                if (!date) {
                    return
                }
                if (typeof(date) == 'string') {
                    // nb. this assumes classic YYYY-MM-DD (ISO) format
                    var parts = date.split('-')
                    return new Date(parts[0], parseInt(parts[1]) - 1, parts[2])
                }
                return date
            },
        },
    }
    Vue.component('wutta-datepicker', WuttaDatepicker)
    <% request.register_component('wutta-datepicker', 'WuttaDatepicker') %>
  </script>
</%def>

<%def name="make_wutta_timepicker_component()">
  <script type="text/x-template" id="wutta-timepicker-template">
    <b-timepicker :name="name"
                  editable
                  :value="buefyValue" />
  </script>
  <script>
    const WuttaTimepicker = {
        template: '#wutta-timepicker-template',
        props: {
            name: String,
            value: String,
            editable: {
                type: Boolean,
                default: true,
            },
        },
        data() {
            return {
                buefyValue: this.parseTime(this.value),
            }
        },
        methods: {

            formatTime(time) {
                if (time === null) {
                    return null
                }

                let h = time.getHours()
                let m = time.getMinutes()
                let s = time.getSeconds()

                h = h < 10 ? '0' + h : h
                m = m < 10 ? '0' + m : m
                s = s < 10 ? '0' + s : s

                return h + ':' + m + ':' + s
            },

            parseTime(time) {
                if (time.getHours) {
                    return time
                }

                let found, hours, minutes

                found = time.match(/^(\d\d):(\d\d):\d\d$/)
                if (found) {
                    hours = parseInt(found[1])
                    minutes = parseInt(found[2])
                    return new Date(null, null, null, hours, minutes)
                }

                found = time.match(/^\s*(\d\d?):(\d\d)\s*([AaPp][Mm])\s*$/)
                if (found) {
                    hours = parseInt(found[1])
                    minutes = parseInt(found[2])
                    const ampm = found[3].toUpperCase()
                    if (ampm == 'AM') {
                        if (hours == 12) {
                            hours = 0
                        }
                    } else { // PM
                        if (hours < 12) {
                            hours += 12
                        }
                    }
                    return new Date(null, null, null, hours, minutes)
                }
            },
        },
    }
    Vue.component('wutta-timepicker', WuttaTimepicker)
    <% request.register_component('wutta-timepicker', 'WuttaTimepicker') %>
  </script>
</%def>

<%def name="make_wutta_filter_component()">
  <script type="text/x-template" id="wutta-filter-template">
    <div v-show="filter.visible"
         class="wutta-filter">

      <b-button @click="filter.active = !filter.active"
                class="filter-toggle"
                icon-pack="fas"
                :icon-left="filter.active ? 'check' : null"
                :size="isSmall ? 'is-small' : null">
        {{ filter.label }}
      </b-button>

      <div v-show="filter.active"
           style="display: flex; gap: 0.5rem;">

        <b-button v-if="verbKnown"
                  class="filter-verb"
                  @click="verbChoiceInit()"
                  :size="isSmall ? 'is-small' : null">
          {{ verbLabel }}
        </b-button>

        <b-autocomplete v-if="!verbKnown"
                        ref="verbAutocomplete"
                        :data="verbOptions"
                        v-model="verbTerm"
                        field="verb"
                        :custom-formatter="formatVerb"
                        open-on-focus
                        keep-first
                        clearable
                        clear-on-select
                        @select="verbChoiceSelect"
                        icon-pack="fas"
                        :size="isSmall ? 'is-small' : null" />

        ## nb. only *ONE* of the following is used, per filter data type

        <wutta-filter-date-value v-if="filter.data_type == 'date'"
                                 v-model="filter.value"
                                 ref="filterValue"
                                 v-show="valuedVerb()"
                                 :is-small="isSmall" />

        <b-select v-if="filter.data_type == 'choice'"
                  v-model="filter.value"
                  ref="filterValue"
                  v-show="valuedVerb()">
          <option v-for="choice in filter.choices"
                  :key="choice"
                  :value="choice">
            {{ filter.choice_labels[choice] || choice }}
          </option>
        </b-select>

        <wutta-filter-value v-else
                            v-model="filter.value"
                            ref="filterValue"
                            v-show="valuedVerb()"
                            :is-small="isSmall" />

      </div>
    </div>
  </script>
  <script>

    const WuttaFilter = {
        template: '#wutta-filter-template',
        props: {
            filter: Object,
            isSmall: Boolean,
        },

        data() {
            return {
                verbKnown: !!this.filter.verb,
                verbLabel: this.filter.verb_labels[this.filter.verb],
                verbTerm: '',
            }
        },

        computed: {

            verbOptions() {

                // construct list of options
                const options = []
                for (let verb of this.filter.verbs) {
                    options.push({
                        verb,
                        label: this.filter.verb_labels[verb],
                    })
                }

                // parse list of search terms
                const terms = []
                for (let term of this.verbTerm.toLowerCase().split(' ')) {
                    term = term.trim()
                    if (term) {
                        terms.push(term)
                    }
                }

                // show all if no search terms
                if (!terms.length) {
                    return options
                }

                // only show filters matching all search terms
                return options.filter(option => {
                    let label = option.label.toLowerCase()
                    for (let term of terms) {
                        if (label.indexOf(term) < 0) {
                            return false
                        }
                    }
                    return true
                })

                return options
            },
        },

        methods: {

            focusValue() {
                this.$refs.filterValue.focus()
            },

            formatVerb(option) {
                return option.label || option.verb
            },

            verbChoiceInit(option) {
                this.verbKnown = false
                this.$nextTick(() => {
                    this.$refs.verbAutocomplete.focus()
                })
            },

            verbChoiceSelect(option) {
                this.filter.verb = option.verb
                this.verbLabel = option.label
                this.verbKnown = true
                this.verbTerm = ''
                this.focusValue()
            },

            valuedVerb() {
                /* return true if the current verb should expose value input(s) */

                // if filter has no "valueless" verbs, then all verbs should expose value inputs
                if (!this.filter.valueless_verbs) {
                    return true
                }

                // if filter *does* have valueless verbs, check if "current" verb is valueless
                if (this.filter.valueless_verbs.includes(this.filter.verb)) {
                    return false
                }

                // current verb is *not* valueless
                return true
            },
        }
    }

    Vue.component('wutta-filter', WuttaFilter)
    <% request.register_component('wutta-filter', 'WuttaFilter') %>
  </script>
</%def>

<%def name="make_wutta_filter_value_component()">
  <script type="text/x-template" id="wutta-filter-value-template">
    <div class="wutta-filter-value">

      <b-input v-model="inputValue"
               ref="valueInput"
               @input="val => $emit('input', val)"
               :size="isSmall ? 'is-small' : null" />

    </div>
  </script>
  <script>

    const WuttaFilterValue = {
        template: '#wutta-filter-value-template',
        props: {
            value: String,
            isSmall: Boolean,
        },

        data() {
            return {
                inputValue: this.value,
            }
        },

        methods: {

            focus: function() {
                this.$refs.valueInput.focus()
            }
        },
    }

    Vue.component('wutta-filter-value', WuttaFilterValue)
    <% request.register_component('wutta-filter-value', 'WuttaFilterValue') %>
  </script>
</%def>

<%def name="make_wutta_filter_date_value_component()">
  <script type="text/x-template" id="wutta-filter-date-value-template">
    <div class="wutta-filter-value">

      <wutta-datepicker v-model="inputValue"
                        ref="valueInput"
                        :size="isSmall ? 'is-small' : null"
                        @input="valueChanged" >
      </wutta-datepicker>

    </div>
  </script>
  <script>

    const WuttaFilterDateValue = {
        template: '#wutta-filter-date-value-template',
        props: {
            value: String,
            isSmall: Boolean,
        },

        data() {
            return {
                inputValue: this.value,
            }
        },

        methods: {

            focus() {
                this.$refs.valueInput.focus()
            },

            valueChanged(value) {
                if (value) {
                    value = this.$refs.valueInput.formatDate(value)
                }
                this.$emit('input', value)
            },
        },
    }

    Vue.component('wutta-filter-date-value', WuttaFilterDateValue)
    <% request.register_component('wutta-filter-date-value', 'WuttaFilterDateValue') %>
  </script>
</%def>

<%def name="make_wutta_tool_panel_component()">
  <script type="text/x-template" id="wutta-tool-panel-template">
    <nav class="panel tool-panel">
      <p class="panel-heading">{{ heading }}</p>
      <div class="panel-block">
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          <slot />
        </div>
      </div>
    </nav>
  </script>
  <script>

    const WuttaToolPanel = {
        template: '#wutta-tool-panel-template',
        props: {
            heading: String,
        },
    }

    Vue.component('wutta-tool-panel', WuttaToolPanel)
    <% request.register_component('wutta-tool-panel', 'WuttaToolPanel') %>
  </script>
</%def>
