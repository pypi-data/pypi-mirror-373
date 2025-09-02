## -*- coding: utf-8; -*-
<%inherit file="/base.mako" />

<%def name="head_title()">${initial_msg or "Working"}...</%def>

<%def name="base_javascript()">
  ${self.core_javascript()}
</%def>

<%def name="base_styles()">
  ${self.core_styles()}
</%def>

<%def name="whole_page_content()">
  <section class="hero is-fullheight">
    <div class="hero-body">
      <div class="container">

        <div style="display: flex;">
          <div style="flex-grow: 1;"></div>
          <div>

            <p class="block">
              {{ progressMessage }} ... {{ totalDisplay }}
            </p>

            <div class="level">

              <div class="level-item">
                <b-progress size="is-large"
                            style="width: 400px;"
                            :max="progressMax"
                            :value="progressValue"
                            show-value
                            format="percent"
                            precision="0">
                </b-progress>
              </div>

            </div>

          </div>
          <div style="flex-grow: 1;"></div>
        </div>

        ${self.after_progress()}

      </div>
    </div>
  </section>
</%def>

<%def name="after_progress()"></%def>

<%def name="modify_vue_vars()">
  <script>

    WholePageData.progressURL = '${url('progress', key=progress.key)}'
    WholePageData.progressMessage = "${(initial_msg or "Working").replace('"', '\\"')} (please wait)"
    WholePageData.progressMax = null
    WholePageData.progressMaxDisplay = null
    WholePageData.progressValue = null
    WholePageData.stillInProgress = true

    WholePage.computed.totalDisplay = function() {

        if (!this.stillInProgress) {
            return "done!"
        }

        if (this.progressMaxDisplay) {
            return `(${'$'}{this.progressMaxDisplay} total)`
        }
    }

    WholePageData.mountedHooks.push(function() {

        // fetch first progress data, one second from now
        setTimeout(() => {
            this.updateProgress()
        }, 1000)
    })

    WholePage.methods.updateProgress = function() {

        this.$http.get(this.progressURL).then(response => {

            if (response.data.error) {
                // errors stop the show; redirect
                location.href = response.data.error_url

            } else {

                if (response.data.complete || response.data.maximum) {
                    this.progressMessage = response.data.message
                    this.progressMaxDisplay = response.data.maximum_display

                    if (response.data.complete) {
                        this.progressValue = this.progressMax
                        this.stillInProgress = false

                        location.href = response.data.success_url

                    } else {
                        this.progressValue = response.data.value
                        this.progressMax = response.data.maximum
                    }
                }

                // custom logic if applicable
                this.updateProgressCustom(response)

                if (this.stillInProgress) {

                    // fetch progress data again, in one second from now
                    setTimeout(() => {
                        this.updateProgress()
                    }, 1000)
                }
            }
        })
    }

    WholePage.methods.updateProgressCustom = function(response) {}

  </script>
</%def>
