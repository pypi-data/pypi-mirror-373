
<%def name="make_http_plugin()">
  <script>

    const HttpPlugin = {

        install(app, options) {
            app.config.globalProperties.$http = {

                get(url, options) {
                    if (options === undefined) {
                        options = {}
                    }

                    if (options.params) {
                        // convert params to query string
                        const data = new URLSearchParams()
                        for (let [key, value] of Object.entries(options.params)) {
                            // nb. all values get converted to string here, so
                            // fallback to empty string to avoid null value
                            // from being interpreted as "null" string
                            if (value === null) {
                                value = ''
                            }
                            data.append(key, value)
                        }
                        // TODO: this should be smarter in case query string already exists
                        url += '?' + data.toString()
                        // params is not a valid arg for options to fetch()
                        delete options.params
                    }

                    return new Promise((resolve, reject) => {
                        fetch(url, options).then(response => {
                            // original response does not contain 'data'
                            // attribute, so must use a "mock" response
                            // which does contain everything
                            response.json().then(json => {
                                resolve({
                                    data: json,
                                    headers: response.headers,
                                    ok: response.ok,
                                    redirected: response.redirected,
                                    status: response.status,
                                    statusText: response.statusText,
                                    type: response.type,
                                    url: response.url,
                                })
                            }, json => {
                                reject(response)
                            })
                        }, response => {
                            reject(response)
                        })
                    })
                },

                post(url, params, options) {

                    if (params) {

                        // attach params as json
                        options.body = JSON.stringify(params)

                        // and declare content-type
                        options.headers = new Headers(options.headers)
                        options.headers.append('Content-Type', 'application/json')
                    }

                    options.method = 'POST'

                    return new Promise((resolve, reject) => {
                        fetch(url, options).then(response => {
                            // original response does not contain 'data'
                            // attribute, so must use a "mock" response
                            // which does contain everything
                            response.json().then(json => {
                                resolve({
                                    data: json,
                                    headers: response.headers,
                                    ok: response.ok,
                                    redirected: response.redirected,
                                    status: response.status,
                                    statusText: response.statusText,
                                    type: response.type,
                                    url: response.url,
                                })
                            }, json => {
                                reject(response)
                            })
                        }, response => {
                            reject(response)
                        })
                    })
                },
            }
        },
    }
  </script>
</%def>
