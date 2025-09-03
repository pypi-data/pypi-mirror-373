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

/**
 * @jest-environment puppeteer
 */

// @ts-ignore
import {ServeFrontend} from '../serve-content.js'

describe('Hello World', () => {
    it('should run a test', () => {
        expect(true).toBe(true);
    });
});

describe('Main Application Flow', () => {
    beforeEach(async () => {
        await page.goto(`http://localhost:${ServeFrontend.port}/static/test.html`);

        // let the graph settle
        await new Promise(resolve => setTimeout(resolve, 2000));
    });

    it('should show the graph', async () => {
        const image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });

    it('should switch to table view', async () => {
        // Click the table button in the top menu
        await page.evaluate(() => {
            const button: HTMLButtonElement | null = document.querySelector('#view-table')
            if (button) {
                button.click();
            }
        });

        const image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });

    it('should switch to schema view', async () => {
        // Click the schema button in the top menu
        await page.evaluate(() => {
            const button: HTMLButtonElement | null = document.querySelector('#view-schema')
            if (button) {
                button.click();
            }
        });

        const image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });
});