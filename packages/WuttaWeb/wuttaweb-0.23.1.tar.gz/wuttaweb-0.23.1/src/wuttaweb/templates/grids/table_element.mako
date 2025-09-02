## -*- coding: utf-8; -*-
<div>

  % if grid.tools:
      <div class="table-tools-wrapper">
        % for html in grid.tools.values():
            ${html}
        % endfor
      </div>
  % endif

<${b}-table :data="gridContext['${grid.key}'].data"

            ## sorting
            % if grid.sortable:
                :default-sort="${grid.get_vue_first_sorter() or 'null'}"
            % endif

            icon-pack="fas">

  % for column in grid.get_vue_columns():
      % if not column['hidden']:
          <${b}-table-column field="${column['field']}"
                             label="${column['label']}"
                             v-slot="props"
                            :sortable="${json.dumps(column.get('sortable', False))|n}"
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

</${b}-table>

</div>
