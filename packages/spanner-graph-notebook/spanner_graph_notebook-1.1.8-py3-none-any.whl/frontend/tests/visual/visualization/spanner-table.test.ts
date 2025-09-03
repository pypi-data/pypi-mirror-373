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

describe('SpannerTable', () => {
    beforeEach(async () => {
        await page.goto('http://localhost:8080/static/test.html');
        await page.evaluate(() => {
            const button: HTMLButtonElement | null = document.querySelector('#view-table')
            if (button) {
                button.click();
            }
        });
    });

    describe('Visibility', () => {
        it('should not be visible in the default graph view', async () => {
            await page.evaluate(() => {
                const button: HTMLButtonElement | null = document.querySelector('#view-default')
                if (button) {
                    button.click();
                }
            });

            const tableElement = await page.$('.spanner-table-wrapper');
            expect(await tableElement.isIntersectingViewport()).toBe(false);

            const image = await page.screenshot();
            expect(Buffer.from(image)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });

        it('should not be visible in the schema view', async () => {
            await page.evaluate(() => {
                const button: HTMLButtonElement | null = document.querySelector('#view-schema')
                if (button) {
                    button.click();
                }
            });

            const tableElement = await page.$('.spanner-table-wrapper');
            expect(await tableElement.isIntersectingViewport()).toBe(false);

            const image = await page.screenshot();
            expect(Buffer.from(image)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });

        it('should be visible in the table view', async () => {
            await page.evaluate(() => {
                const button: HTMLButtonElement | null = document.querySelector('#view-table')
                if (button) {
                    button.click();
                }
            });

            const tableElement = await page.$('.spanner-table-wrapper');
            expect(await tableElement.isIntersectingViewport()).toBe(true);

            const image = await page.screenshot();
            expect(Buffer.from(image)).toMatchImageSnapshot({
                failureThreshold: 0.05,
                failureThresholdType: 'percent'
            });
        });
    });

    it('should show visual difference between expanded and collapsed rows', async () => {
        // Capture initial state
        let image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });

        // Click expand on first row with truncated content
        await page.evaluate(() => {
            const expandIcon = document.querySelector('.expand-icon');
            if (expandIcon) expandIcon.click();
        });
        await new Promise(resolve => setTimeout(resolve, 500));

        // Capture expanded state
        image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });

    it('should be horizontally scrollable and maintain visual consistency when scrolled', async () => {
        // Get the table wrapper element
        const tableWrapper = await page.$('.spanner-table-wrapper');
        expect(tableWrapper).toBeTruthy();

        // Take screenshot of initial state
        let image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });

        // Scroll to the rightmost edge
        await page.evaluate(() => {
            const wrapper = document.querySelector('.spanner-table-wrapper');
            if (wrapper) {
                wrapper.scrollLeft = wrapper.scrollWidth - wrapper.clientWidth;
            }
        });

        // Wait for any potential scroll animations
        await new Promise(resolve => setTimeout(resolve, 500));

        // Verify scroll position
        const scrollPosition = await page.evaluate(() => {
            const wrapper = document.querySelector('.spanner-table-wrapper');
            return {
                scrollLeft: wrapper.scrollLeft,
                scrollWidth: wrapper.scrollWidth,
                clientWidth: wrapper.clientWidth
            };
        });

        // Ensure we actually scrolled (scrollLeft should be > 0)
        expect(scrollPosition.scrollLeft).toBeGreaterThan(0);

        // Ensure we scrolled all the way (scrollLeft should be scrollWidth - clientWidth)
        const withinTolerance = Math.abs(scrollPosition.scrollLeft - (scrollPosition.scrollWidth - scrollPosition.clientWidth)) < 1;
        expect(withinTolerance).toBe(true);

        // Take screenshot of scrolled state
        image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });

    it('should keep expand column visible when scrolled horizontally', async () => {
        // Scroll to the rightmost edge
        await page.evaluate(() => {
            const wrapper = document.querySelector('.spanner-table-wrapper');
            if (wrapper) {
                wrapper.scrollLeft = wrapper.scrollWidth - wrapper.clientWidth;
            }
        });

        // Wait for any potential scroll animations
        await new Promise(resolve => setTimeout(resolve, 500));

        // Verify expand column is still visible
        const expandColumnVisible = await page.evaluate(() => {
            const expandColumn = document.querySelector('.expand-column');
            if (!expandColumn) return false;

            const rect = expandColumn.getBoundingClientRect();
            const wrapper = document.querySelector('.spanner-table-wrapper');
            const wrapperRect = wrapper.getBoundingClientRect();

            return rect.right <= wrapperRect.right && rect.left >= wrapperRect.left;
        });

        expect(expandColumnVisible).toBe(true);

        // Take screenshot to verify expand column visibility
        const image = await page.screenshot();
        expect(Buffer.from(image)).toMatchImageSnapshot({
            failureThreshold: 0.05,
            failureThresholdType: 'percent'
        });
    });
});