
<%def name="make_buefy_plugin()">
  <script>

    const BuefyPlugin = {
        install(app, options) {
            app.config.globalProperties.$buefy = {

                toast: {
                    open(options) {

                        let variant = null
                        if (options.type) {
                            variant = options.type.replace(/^is-/, '')
                        }

                        const opts = {
                            duration: options.duration,
                            message: options.message,
                            position: 'top',
                            variant,
                        }

                        const oruga = app.config.globalProperties.$oruga
                        oruga.notification.open(opts)
                    },
                },
            }
        },
    }
  </script>
</%def>
