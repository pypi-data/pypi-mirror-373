/**
 * Copyright 2025 Google LLC
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *
 */

module.exports = {
    server: {
        // How you build your bundle. If you use Rollup, add the plugin rollup-plugin-serve with the configuration serve({ contentBase: ‘dist’, port: 10002 })
        command: `http-server -p 8080 -c-1`,
        port: 8080,
        // if default or tcp, the test starts right await whereas the dev server is not available on http
        protocol: 'http',
        // in ms
        launchTimeout: 30000,
        debug: true,
    },
    launch: {
        dumpio: true,
        headless: process.env.HEADLESS !== 'false',
        args: ['--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox'],
        timeout: 120000,
    },
};