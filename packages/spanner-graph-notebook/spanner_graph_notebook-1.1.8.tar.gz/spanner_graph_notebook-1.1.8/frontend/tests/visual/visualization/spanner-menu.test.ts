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

// @ts-ignore
import GraphConfig from "../../../src/spanner-config";

describe('SpannerMenu', () => {
    beforeEach(async () => {
        await page.goto('http://localhost:8080/static/test.html');
        // let the graph settle
        await new Promise(resolve => setTimeout(resolve, 2000));
    });

    describe('Menu Structure', () => {
        it('should properly scaffold the menu structure', async () => {
            const menuBar = await page.$('.menu-bar');
            const viewToggleGroup = await page.$('.view-toggle-group');
            const dropdown = await page.$('.dropdown');
            const elementCount = await page.$('.element-count');
            const labelsContainer = await page.$('#show-labels-container');

            expect(menuBar).toBeTruthy();
            expect(viewToggleGroup).toBeTruthy();
            expect(dropdown).toBeTruthy();
            expect(elementCount).toBeTruthy();
            expect(labelsContainer).toBeTruthy();

            const image = await page.screenshot();
            expect(Buffer.from(image)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });
    });

    describe('View Mode Controls', () => {
        it('should switch between different view modes', async () => {
            // Test default view
            const defaultImage = await page.screenshot();
            expect(Buffer.from(defaultImage)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });

            // Switch to table view
            await page.evaluate(() => {
                const button = document.querySelector('#view-table') as HTMLButtonElement;
                if (button) button.click();
            });
            await new Promise(resolve => setTimeout(resolve, 1000));
            const tableImage = await page.screenshot();
            expect(Buffer.from(tableImage)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });

            // Switch to schema view
            await page.evaluate(() => {
                const button = document.querySelector('#view-schema') as HTMLButtonElement;
                if (button) button.click();
            });
            await new Promise(resolve => setTimeout(resolve, 1000));
            const schemaImage = await page.screenshot();
            expect(Buffer.from(schemaImage)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });
    });

    describe('Layout Controls', () => {
        for (const key in GraphConfig.LayoutModes) {
            const layout = GraphConfig.LayoutModes[key].description;

            it(`should change layout mode to ${layout}`, async () => {
                await page.evaluate(layout => {
                    const layoutButton = document.querySelector(`[data-layout="${layout}"]`) as HTMLElement;
                    if (layoutButton) {
                        layoutButton.click();
                    }
                }, layout);

                await new Promise(resolve => setTimeout(resolve, 1000));

                const image = await page.screenshot();
                expect(Buffer.from(image)).toMatchImageSnapshot({
                    failureThreshold: 0.05,
                    failureThresholdType: 'percent'
                });
            })
        }
    });

    describe('Label Controls', () => {
        it('should toggle label visibility', async () => {
            // Initial state without labels
            const withoutLabels = await page.screenshot();
            expect(Buffer.from(withoutLabels)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });

            // Toggle labels on
            await page.evaluate(() => {
                const labelSwitch = document.querySelector('#show-labels') as HTMLInputElement;
                if (labelSwitch) {
                    labelSwitch.checked = true;
                    labelSwitch.dispatchEvent(new Event('change'));
                }
            });
            await new Promise(resolve => setTimeout(resolve, 1000));

            const withLabels = await page.screenshot();
            expect(Buffer.from(withLabels)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });
    });

    describe('Fullscreen Controls', () => {
        it('should only be visible in the table view mode', async () => {
            // The application is expected to show the graph view upon page load,
            // and as such the fullscreen button should exist but not be visible
            let fullscreenButton = await page.$('.fullscreen-button');
            expect(fullscreenButton).toBeTruthy();
            expect(await fullscreenButton.isIntersectingViewport()).toBeFalsy();

            // Switch to table view, expect it to be visible, and take a snapshot
            await page.evaluate(() => {
                const button = document.querySelector('#view-table') as HTMLButtonElement;
                if (button) button.click();

            });
            fullscreenButton = await page.$('.fullscreen-button');
            expect(await fullscreenButton.isIntersectingViewport()).toBeTruthy();
            const tableImage = await page.screenshot();
            expect(Buffer.from(tableImage)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });

            // Switch to schema view and expect it to be invisible
            await page.evaluate(() => {
                const button = document.querySelector('#view-schema') as HTMLButtonElement;
                if (button) button.click();
            });
            fullscreenButton = await page.$('.fullscreen-button');
            expect(await fullscreenButton.isIntersectingViewport()).toBeFalsy();
        });
    });
})
;
