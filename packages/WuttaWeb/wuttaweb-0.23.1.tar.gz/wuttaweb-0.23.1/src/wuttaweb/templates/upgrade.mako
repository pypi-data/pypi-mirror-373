## -*- coding: utf-8; -*-
<%inherit file="/progress.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>

    .upgrade-textout {
        border: 1px solid Black;
        line-height: 1.2;
        margin-top: 1rem;
        overflow: auto;
        padding: 1rem;
    }

  </style>
</%def>

<%def name="after_progress()">
  <div ref="textout"
       class="upgrade-textout is-family-monospace is-size-7">
    <span v-for="line in progressOutput"
          :key="line.key"
          v-html="line.text">
    </span>

    ## nb. we auto-scroll down to "see" this element
    <div ref="seeme"></div>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    WholePageData.progressURL = '${url('upgrades.execute_progress', uuid=instance.uuid)}'
    WholePageData.progressOutput = []
    WholePageData.progressOutputCounter = 0

    WholePageData.mountedHooks.push(function() {

        // grow the textout area to fill most of screen
        const textout = this.$refs.textout
        const height = window.innerHeight - textout.offsetTop - 100
        textout.style.height = height + 'px'
    })

    WholePage.methods.updateProgressCustom = function(response) {
        if (response.data.stdout) {

            // add lines to textout area
            this.progressOutput.push({
                key: ++this.progressOutputCounter,
                text: response.data.stdout})

            //  scroll down to end of textout area
            this.$nextTick(() => {
                this.$refs.seeme.scrollIntoView({behavior: 'smooth'})
            })
        }
    }

  </script>
</%def>
