## -*- coding: utf-8; -*-

<script type="text/x-template" id="${grid.vue_tagname}-template">
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5em;">

      % if grid.filterable:
          <form @submit.prevent="applyFilters()">

            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              <wutta-filter v-for="filtr in filters"
                            :key="filtr.key"
                            :filter="filtr"
                            :is-small="smallFilters"
                            ref="gridFilters" />

              <div style="display: flex; gap: 0.5rem;">

                <b-button @click="copyDirectLink()"
                          title="Copy grid link to clipboard"
                          :is-small="smallFilters">
                  <b-icon pack="fas" icon="share" />
                </b-button>

                <b-button type="is-primary"
                          native-type="submit"
                          icon-pack="fas"
                          icon-left="filter"
                          :size="smallFilters ? 'is-small' : null">
                  Apply Filters
                </b-button>

                <div>
                  <b-button v-if="!addFilterShow"
                            @click="addFilterInit()"
                            icon-pack="fas"
                            icon-left="plus"
                            :size="smallFilters ? 'is-small' : null">
                    Add Filter
                  </b-button>
                  <b-autocomplete v-if="addFilterShow"
                                  ref="addFilterAutocomplete"
                                  :data="addFilterChoices"
                                  v-model="addFilterTerm"
                                  placeholder="Add Filter"
                                  field="key"
                                  :custom-formatter="formatAddFilterItem"
                                  open-on-focus
                                  keep-first
                                  clearable
                                  clear-on-select
                                  @select="addFilterSelect"
                                  icon-pack="fas"
                                  :size="smallFilters ? 'is-small' : null" />
                </div>

                <b-button @click="resetView()"
                          :disabled="viewResetting"
                          icon-pack="fas"
                          icon-left="undo"
                          :size="smallFilters ? 'is-small' : null">
                  {{ viewResetting ? "Working, please wait..." : "Reset View" }}
                </b-button>

                <b-button v-show="activeFilters"
                          @click="clearFilters()"
                          icon-pack="fas"
                          icon-left="trash"
                          :size="smallFilters ? 'is-small' : null">
                  No Filters
                </b-button>

          ## TODO: this semi-works but is not persisted for user
          ##       <b-button v-if="!smallFilters"
          ##                 @click="smallFilters = true"
          ##                 icon-pack="fas"
          ##                 icon-left="compress"
          ##                 title="toggle filter size" />
          ##
          ##       <span v-if="smallFilters">
          ##         <b-button @click="smallFilters = false"
          ##                   icon-pack="fas"
          ##                   icon-left="expand"
          ##                   size="is-small"
          ##                   title="toggle filter size" />
          ##       </span>

              </div>

            </div>
          </form>

      % else:
          <div></div>
      % endif

      <div style="display: flex; flex-direction: column; justify-content: space-between;">

        ## nb. this is needed to force tools to bottom
        ## TODO: should we put a context menu here?
        <div></div>

        <div class="wutta-grid-tools-wrapper">
          % for html in grid.tools.values():
              ${html}
          % endfor
        </div>
      </div>

    </div>

    <${b}-table :data="data"
                :row-class="getRowClass"
                :loading="loading"
                narrowed
                hoverable
                icon-pack="fas"

                ## checkboxes
                % if grid.checkable:
                    checkable
                    checkbox-position="right"
                    :checked-rows.sync="checkedRows"
                % endif

                ## sorting
                % if grid.sortable:
                    ## nb. buefy/oruga only support *one* default sorter
                    :default-sort="sorters.length ? [sorters[0].field, sorters[0].order] : null"
                    % if grid.sort_on_backend:
                        backend-sorting
                        @sort="onSort"
                    % endif
                    % if grid.sort_multiple:
                        % if grid.sort_on_backend:
                            ## TODO: there is a bug (?) which prevents the arrow
                            ## from displaying for simple default single-column sort,
                            ## when multi-column sort is allowed for the table.  for
                            ## now we work around that by waiting until mount to
                            ## enable the multi-column support.  see also
                            ## https://github.com/buefy/buefy/issues/2584
                            :sort-multiple="allowMultiSort"
                            :sort-multiple-data="sortingPriority"
                            @sorting-priority-removed="sortingPriorityRemoved"
                        % else:
                            sort-multiple
                        % endif
                        ## nb. user must ctrl-click column header for multi-sort
                        sort-multiple-key="ctrlKey"
                    % endif
                % endif

                ## paging
                % if grid.paginated:
                    paginated
                    pagination-size="${'small' if request.use_oruga else 'is-small'}"
                    :per-page="perPage"
                    :current-page="currentPage"
                    @page-change="onPageChange"
                    % if grid.paginate_on_backend:
                        backend-pagination
                        :total="pagerStats.item_count"
                    % endif
                % endif
                >

      % for column in grid.get_vue_columns():
          % if not column['hidden']:
              <${b}-table-column field="${column['field']}"
                                 label="${column['label']}"
                                 v-slot="props"
                                :sortable="${json.dumps(column.get('sortable', False))|n}"
                                :searchable="${json.dumps(column.get('searchable', False))|n}"
                                 cell-class="c_${column['field']}">
                % if grid.is_linked(column['field']):
                    <a :href="props.row._action_url_view"
                       v-html="props.row.${column['field']}" />
                % else:
                    <span v-html="props.row.${column['field']}"></span>
                % endif
              </${b}-table-column>
          % endif
      % endfor

      % if grid.actions:
          <${b}-table-column field="actions"
                             label="Actions"
                             v-slot="props">
            % for action in grid.actions:
                <a v-if="props.row._action_url_${action.key}"
                   :href="props.row._action_url_${action.key}"
                   % if action.target:
                       target="${action.target}"
                   % endif
                   % if action.click_handler:
                       @click.prevent="${action.click_handler}"
                   % endif
                   class="${action.link_class}">
                  ${action.render_icon_and_label()}
                </a>
                &nbsp;
            % endfor
          </${b}-table-column>
      % endif

      <template #empty>
        <section class="section">
          <div class="content has-text-grey has-text-centered">
            <p>
              <b-icon
                 pack="fas"
                 icon="sad-tear"
                 size="is-large">
              </b-icon>
            </p>
            <p>Nothing here.</p>
          </div>
        </section>
      </template>

      % if grid.paginated:
          <template #footer>
            <div style="display: flex; justify-content: space-between;">
              <div></div>
              <div v-if="pagerStats.first_item"
                   style="display: flex; gap: 0.5rem; align-items: center;">
                <span>
                  showing
                  {{ renderNumber(pagerStats.first_item) }}
                  - {{ renderNumber(pagerStats.last_item) }}
                  of {{ renderNumber(pagerStats.item_count) }} results;
                </span>
                <b-select v-model="perPage"
                          % if grid.paginate_on_backend:
                              @input="onPageSizeChange"
                          % endif
                          size="is-small">
                  <option v-for="size in pageSizeOptions"
                          :value="size">
                    {{ size }}
                  </option>
                </b-select>
                <span>
                  per page
                </span>
              </div>
            </div>
          </template>
        % endif

    </${b}-table>

    ## dummy input field needed for sharing links on *insecure* sites
    % if getattr(request, 'scheme', None) == 'http':
        <b-input v-model="shareLink" ref="shareLink" v-show="shareLink"></b-input>
    % endif

  </div>
</script>

<script>

  const ${grid.vue_component}Context = ${json.dumps(grid.get_vue_context())|n}
  let ${grid.vue_component}CurrentData = ${grid.vue_component}Context.data

  const ${grid.vue_component}Data = {
      data: ${grid.vue_component}CurrentData,
      rowClasses: ${grid.vue_component}Context.row_classes,
      loading: false,

      ## nb. this tracks whether grid.fetchFirstData() happened
      fetchedFirstData: false,

      ## dummy input value needed for sharing links on *insecure* sites
      % if getattr(request, 'scheme', None) == 'http':
          shareLink: null,
      % endif

      ## checkboxes
      % if grid.checkable:
          checkedRows: [],
      % endif

      ## filtering
      % if grid.filterable:
          filters: ${json.dumps(grid.get_vue_filters())|n},
          addFilterShow: false,
          addFilterTerm: '',
          smallFilters: false,
          viewResetting: false,
      % endif

      ## sorting
      % if grid.sortable:
          sorters: ${json.dumps(grid.get_vue_active_sorters())|n},
          % if grid.sort_multiple:
              % if grid.sort_on_backend:
                  ## TODO: there is a bug (?) which prevents the arrow
                  ## from displaying for simple default single-column sort,
                  ## when multi-column sort is allowed for the table.  for
                  ## now we work around that by waiting until mount to
                  ## enable the multi-column support.  see also
                  ## https://github.com/buefy/buefy/issues/2584
                  allowMultiSort: false,
                  ## nb. this should be empty when current sort is single-column
                  % if len(grid.active_sorters) > 1:
                      sortingPriority: ${json.dumps(grid.get_vue_active_sorters())|n},
                  % else:
                      sortingPriority: [],
                  % endif
              % endif
          % endif
      % endif

      ## paging
      % if grid.paginated:
          pageSizeOptions: ${json.dumps(grid.pagesize_options)|n},
          perPage: ${json.dumps(grid.pagesize)|n},
          currentPage: ${json.dumps(grid.page)|n},
          % if grid.paginate_on_backend:
              pagerStats: ${json.dumps(grid.get_vue_pager_stats())|n},
          % endif
      % endif
  }

  const ${grid.vue_component} = {
      template: '#${grid.vue_tagname}-template',
      computed: {

          recordCount() {
              % if grid.paginated:
                  return this.pagerStats.item_count
              % else:
                  return this.data.length
              % endif
          },

          directLink() {
              const params = new URLSearchParams(this.getAllParams())
              return `${request.path_url}?${'$'}{params}`
          },

          % if grid.filterable:

              addFilterChoices() {

                  // parse list of search terms
                  const terms = []
                  for (let term of this.addFilterTerm.toLowerCase().split(' ')) {
                      term = term.trim()
                      if (term) {
                          terms.push(term)
                      }
                  }

                  // show all if no search terms
                  if (!terms.length) {
                      return this.filters
                  }

                  // only show filters matching all search terms
                  return this.filters.filter(option => {
                      let label = option.label.toLowerCase()
                      for (let term of terms) {
                          if (label.indexOf(term) < 0) {
                              return false
                          }
                      }
                      return true
                  })
              },

              activeFilters() {
                  for (let filtr of this.filters) {
                      if (filtr.active) {
                          return true
                      }
                  }
                  return false
              },

          % endif

          % if not grid.paginate_on_backend:

              pagerStats() {
                  const data = this.data
                  let last = this.currentPage * this.perPage
                  let first = last - this.perPage + 1
                  if (last > data.length) {
                      last = data.length
                  }
                  return {
                      'item_count': data.length,
                      'items_per_page': this.perPage,
                      'page': this.currentPage,
                      'first_item': first,
                      'last_item': last,
                  }
              },

          % endif
      },

      % if grid.sortable and grid.sort_multiple and grid.sort_on_backend:

            ## TODO: there is a bug (?) which prevents the arrow
            ## from displaying for simple default single-column sort,
            ## when multi-column sort is allowed for the table.  for
            ## now we work around that by waiting until mount to
            ## enable the multi-column support.  see also
            ## https://github.com/buefy/buefy/issues/2584
            mounted() {
                this.allowMultiSort = true
            },

      % endif

      methods: {

          copyDirectLink() {

              if (navigator.clipboard) {
                  // this is the way forward, but requires HTTPS
                  navigator.clipboard.writeText(this.directLink)

              } else {
                  // use deprecated 'copy' command, but this just
                  // tells the browser to copy currently-selected
                  // text..which means we first must "add" some text
                  // to screen, and auto-select that, before copying
                  // to clipboard
                  this.shareLink = this.directLink
                  this.$nextTick(() => {
                      let input = this.$refs.shareLink.$el.firstChild
                      input.select()
                      document.execCommand('copy')
                      // re-hide the dummy input
                      this.shareLink = null
                  })
              }

              this.$buefy.toast.open({
                  message: "Link was copied to clipboard",
                  type: 'is-info',
                  duration: 2000, // 2 seconds
              })
          },

          getRowClass(row, i) {
              // nb. use *string* index
              return this.rowClasses[i.toString()]
          },

          renderNumber(value) {
              if (value != undefined) {
                  return value.toLocaleString('en')
              }
          },

          getAllParams() {
              return {
                  ...this.getBasicParams(),
                  % if grid.filterable:
                      ...this.getFilterParams(),
                  % endif
              }
          },

          getBasicParams() {
              const params = {
                  % if grid.paginated and grid.paginate_on_backend:
                      pagesize: this.perPage,
                      page: this.currentPage,
                  % endif
              }
              % if grid.sortable and grid.sort_on_backend:
                  for (let i = 1; i <= this.sorters.length; i++) {
                      params['sort'+i+'key'] = this.sorters[i-1].field
                      params['sort'+i+'dir'] = this.sorters[i-1].order
                  }
              % endif
              return params
          },

          ## nb. this is meant to call for a grid which is hidden at
          ## first, when it is first being shown to the user.  and if
          ## it was initialized with empty data set.
          async fetchFirstData() {
              if (this.fetchedFirstData) {
                  return
              }
              await this.fetchData()
              this.fetchedFirstData = true
          },

          async fetchData(params) {
              if (params === undefined || params === null) {
                  params = this.getBasicParams()
              }

              params = new URLSearchParams(params)
              if (!params.has('partial')) {
                  params.append('partial', true)
              }
              params = params.toString()

              this.loading = true
              this.$http.get(`${request.path_url}?${'$'}{params}`).then(response => {
                  if (!response.data.error) {
                      ${grid.vue_component}CurrentData = response.data.data
                      this.data = ${grid.vue_component}CurrentData
                      this.rowClasses = response.data.row_classes || {}
                      % if grid.paginated and grid.paginate_on_backend:
                          this.pagerStats = response.data.pager_stats
                      % endif
                      this.loading = false
                  } else {
                      this.$buefy.toast.open({
                          message: data.error,
                          type: 'is-danger',
                          duration: 2000, // 4 seconds
                      })
                      this.loading = false
                  }
              })
              .catch((error) => {
                  this.data = []
                  % if grid.paginated and grid.paginate_on_backend:
                      this.pagerStats = {}
                  % endif
                  this.loading = false
                  throw error
              })
          },

          resetView() {
              this.viewResetting = true
              this.loading = true

              // use current url proper, plus reset param
              let url = '?reset-view=true'

              // add current hash, to preserve that in redirect
              if (location.hash) {
                  url += '&hash=' + location.hash.slice(1)
              }

              location.href = url
          },

          % if grid.filterable:

              formatAddFilterItem(filtr) {
                  return filtr.label || filtr.key
              },

              addFilterInit() {
                  this.addFilterShow = true
                  this.$nextTick(() => {
                      const input = this.$refs.addFilterAutocomplete.$el.querySelector('input')
                      input.addEventListener('keydown', this.addFilterKeydown)
                      this.$refs.addFilterAutocomplete.focus()
                  })
              },

              addFilterKeydown(event) {

                  // ESC will clear searchbox
                  if (event.which == 27) {
                      this.addFilterHide()
                  }
              },

              addFilterHide() {
                  const input = this.$refs.addFilterAutocomplete.$el.querySelector('input')
                  input.removeEventListener('keydown', this.addFilterKeydown)
                  this.addFilterTerm = ''
                  this.addFilterShow = false
              },

              addFilterSelect(filtr) {
                  this.addFilter(filtr.key)
                  this.addFilterHide()
              },

              findFilter(key) {
                  for (let filtr of this.filters) {
                      if (filtr.key == key) {
                          return filtr
                      }
                  }
              },

              findFilterComponent(key) {
                  for (let filtr of this.$refs.gridFilters) {
                      if (filtr.filter.key == key) {
                          return filtr
                      }
                  }
              },

              addFilter(key) {

                  // show the filter
                  let filtr = this.findFilter(key)
                  filtr.active = true
                  filtr.visible = true

                  // focus the filter
                  filtr = this.findFilterComponent(key)
                  this.$nextTick(() => {
                      filtr.focusValue()
                  })
              },

              clearFilters() {

                  // explicitly deactivate all filters
                  for (let filter of this.filters) {
                      filter.active = false
                  }

                  // then just "apply" as normal
                  this.applyFilters()
              },

              applyFilters(params) {
                  if (params === undefined) {
                      params = this.getFilterParams()
                  }

                  // hide inactive filters
                  for (let filter of this.filters) {
                      if (!filter.active) {
                          filter.visible = false
                      }
                  }

                  // fetch new data
                  params.filter = true
                  this.fetchData(params)
              },

              getFilterParams() {
                  const params = {}
                  for (let filter of this.filters) {
                      if (filter.active) {
                          params[filter.key] = filter.value
                          params[filter.key+'.verb'] = filter.verb
                      }
                  }
                  if (Object.keys(params).length) {
                      params.filter = 'true'
                  }
                  return params
              },

          % endif

          % if grid.sortable and grid.sort_on_backend:

              onSort(field, order, event) {

                  ## nb. buefy passes field name; oruga passes field object
                  % if request.use_oruga:
                      field = field.field
                  % endif

                  % if grid.sort_multiple:

                      // did user ctrl-click the column header?
                      if (event.ctrlKey) {

                          // toggle direction for existing, or add new sorter
                          const sorter = this.sorters.filter(s => s.field === field)[0]
                          if (sorter) {
                              sorter.order = sorter.order === 'desc' ? 'asc' : 'desc'
                          } else {
                              this.sorters.push({field, order})
                          }

                          // apply multi-column sorting
                          this.sortingPriority = this.sorters

                      } else {

                  % endif

                  // sort by single column only
                  this.sorters = [{field, order}]

                  % if grid.sort_multiple:
                          // multi-column sort not engaged
                          this.sortingPriority = []
                      }
                  % endif

                  // nb. always reset to first page when sorting changes
                  this.currentPage = 1
                  this.fetchData()
              },

              % if grid.sort_multiple:

                  sortingPriorityRemoved(field) {

                      // prune from active sorters
                      this.sorters = this.sorters.filter(s => s.field !== field)

                      // nb. even though we might have just one sorter
                      // now, we are still technically in multi-sort mode
                      this.sortingPriority = this.sorters

                      this.fetchData()
                  },

              % endif

          % endif

          % if grid.paginated:

              % if grid.paginate_on_backend:
                  onPageSizeChange(size) {
                      this.fetchData()
                  },
              % endif

              onPageChange(page) {
                  this.currentPage = page
                  % if grid.paginate_on_backend:
                      this.fetchData()
                  % endif
              },

          % endif
      },
  }

</script>

<% request.register_component(grid.vue_tagname, grid.vue_component) %>
