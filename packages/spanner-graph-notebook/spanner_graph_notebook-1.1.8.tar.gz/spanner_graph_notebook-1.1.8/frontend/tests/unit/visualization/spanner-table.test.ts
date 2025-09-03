// @ts-nocheck
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

import GraphStore from '../../../src/spanner-store';
import GraphConfig from '../../../src/spanner-config';
import mockData from '../../mock-data.json';
import SpannerTable from '../../../src/visualization/spanner-table';

describe('SpannerTable', () => {
    let store;
    let mockConfig;
    let mount;
    let menuMount;
    let spannerTable;

    beforeEach(() => {
        // Mock the DOM mount points
        mount = document.createElement('div');
        mount.id = 'table-mount';
        menuMount = document.createElement('div');
        document.body.appendChild(mount);
        document.body.appendChild(menuMount);

        // Set up store with mock config using actual mock data
        mockConfig = new GraphConfig({
            nodesData: mockData.response.nodes,
            edgesData: mockData.response.edges,
            colorScheme: GraphConfig.ColorScheme.LABEL,
            viewMode: GraphConfig.ViewModes.TABLE,
            schemaData: mockData.response.schema,
            queryResult: {
                column1: [{ value: 'data1' }, { value: 'data2' }],
                column2: [{ value: 'data3' }, { value: 'data4' }]
            }
        });

        store = new GraphStore(mockConfig);
        spannerTable = new SpannerTable(store, mount, menuMount);
    });

    afterEach(() => {
        document.body.removeChild(mount);
        document.body.removeChild(menuMount);
    });

    describe('Initialization', () => {
        test('should properly initialize with store and mount elements', () => {
            expect(spannerTable.store).toBe(store);
            expect(spannerTable.mount).toBe(mount);
            expect(spannerTable.menuMount).toBe(menuMount);
        });

        test('should initialize with correct default values', () => {
            expect(spannerTable.currentPage).toBe(0);
            expect(spannerTable.rowsPerPage).toBe(50);
            expect(spannerTable.expandedRows).toBeInstanceOf(Set);
            expect(spannerTable.expandedRows.size).toBe(0);
        });
    });

    describe('Table Header Creation', () => {
        test('should create table headers from query result', () => {
            spannerTable.render();
            const headers = mount.querySelectorAll('table th');
            const queryColumns = Object.keys(store.config.queryResult);
            
            // +1 for expand column
            expect(headers.length).toBe(queryColumns.length + 1);
            
            queryColumns.forEach((column, index) => {
                expect(headers[index].textContent).toBe(column);
            });
        });

        test('should handle non-string header fields', () => {
            store.config.queryResult = {
                1: [{ value: 'test' }],
                true: [{ value: 'test' }]
            };
            spannerTable.render();
            const headers = mount.querySelectorAll('table th');
            expect(headers[0].textContent).toBe('1');
            expect(headers[1].textContent).toBe('true');
        });
    });

    describe('Data Transformation', () => {
        test('parseQueryResultToRows transforms data correctly', () => {
            spannerTable.parseQueryResultToRows();
            expect(spannerTable.rows).toHaveLength(2);
            expect(spannerTable.rows[0]).toHaveLength(2);
            expect(spannerTable.rows[0][0]).toEqual({ value: 'data1' });
            expect(spannerTable.rows[1][1]).toEqual({ value: 'data4' });
        });

        test('handles empty query result', () => {
            store.config.queryResult = {};
            spannerTable.parseQueryResultToRows();
            expect(spannerTable.rows).toHaveLength(0);
        });

        test('handles malformed query result', () => {
            store.config.queryResult = null;
            spannerTable.render();
            const errorDiv = mount.querySelector('.table-error');
            expect(errorDiv?.classList.contains('hidden')).toBe(false);
        });
    });

    describe('Cell Formatting', () => {
        test('formatCellContent handles different data types', () => {
            const testCases = [
                { input: 'simple string', expected: { content: 'simple string', truncated: false } },
                { input: { key: 'value' }, expected: { content: '{"key":"value"}', truncated: false } },
                { input: null, expected: { content: '', truncated: false } },
                { input: undefined, expected: { content: '', truncated: false } },
                { 
                    input: 'a'.repeat(100), 
                    expected: { 
                        content: 'a'.repeat(77) + '...', 
                        truncated: true 
                    } 
                }
            ];

            testCases.forEach(({ input, expected }) => {
                const result = spannerTable.formatCellContent(input, 0);
                expect(result).toEqual(expected);
            });
        });

        test('handles row expansion correctly', () => {
            spannerTable.expandedRows.add(0);
            const longString = 'a'.repeat(100);
            const result = spannerTable.formatCellContent(longString, 0);
            expect(result.truncated).toBe(false);
            expect(result.content).toBe(longString);
        });
    });

    describe('Row Expansion UI', () => {
        beforeEach(() => {
            store.config.queryResult = {
                column1: [{ value: 'a'.repeat(100) }]
            };
            spannerTable.parseQueryResultToRows();
            spannerTable.render();
        });

        test('should show expansion arrow for truncated content', () => {
            const expandIcon = mount.querySelector('.expand-icon');
            expect(expandIcon).not.toBeNull();
        });

        test('should toggle row expansion on click', () => {
            const row = mount.querySelector('tbody tr');
            const expandIcon = row.querySelector('.expand-icon');

            // the returned HTML has an added <path> element
            const normalizeSvg = (svg) => svg.replace(/\/>/g, '></path>');

            // Initial state check
            expect(spannerTable.expandedRows.size).toBe(0);
            expect(row.classList.contains('expanded')).toBe(false);
            
            // First click - expand
            expandIcon.click();
            expect(spannerTable.expandedRows.size).toBe(1);
            expect(spannerTable.expandedRows.has(0)).toBe(true);
            expect(row.classList.contains('expanded')).toBe(true);
            expect(normalizeSvg(expandIcon.innerHTML)).toBe(normalizeSvg(spannerTable.svg.down));
            
            // Second click - collapse
            expandIcon.click();
            expect(spannerTable.expandedRows.size).toBe(0);
            expect(spannerTable.expandedRows.has(0)).toBe(false);
            expect(row.classList.contains('expanded')).toBe(false);
            expect(normalizeSvg(expandIcon.innerHTML)).toBe(normalizeSvg(spannerTable.svg.up));
        });

        test('should not show expansion arrow for non-truncated content', () => {
            store.config.queryResult = {
                column1: [{ value: 'short' }]
            };
            spannerTable.parseQueryResultToRows();
            spannerTable.render();
            
            const expandIcon = mount.querySelector('.expand-icon');
            expect(expandIcon).toBeNull();
        });
    });

    describe('Pagination', () => {
        beforeEach(() => {
            store.config.queryResult = {
                column1: Array(100).fill({ value: 'test' })
            };
            spannerTable.parseQueryResultToRows();
            spannerTable.render();
        });

        test('updates current page correctly', () => {
            spannerTable.goToPage(1);
            expect(spannerTable.currentPage).toBe(1);
        });

        test('handles page bounds', () => {
            spannerTable.goToPage(100);
            expect(spannerTable.currentPage).toBe(100);
        });

        test('renders correct number of rows per page', () => {
            const tableRows = mount.querySelectorAll('table tr');
            // +1 for header row
            expect(tableRows.length).toBe(spannerTable.rowsPerPage + 1);
        });

        test('pagination controls render correctly', () => {
            const controls = mount.querySelector('.pagination-controls');
            expect(controls).not.toBeNull();
            
            const rowsPerPage = controls.querySelector('.rows-per-page select');
            expect(rowsPerPage).not.toBeNull();
            expect(rowsPerPage.value).toBe('50');
            
            const range = controls.querySelector('.pagination-range');
            expect(range.textContent).toBe('1–50 of 100');
            
            const arrows = controls.querySelectorAll('.pagination-arrow');
            expect(arrows.length).toBe(4);
        });

        test('pagination controls update on page change', () => {
            spannerTable.goToPage(1);
            const range = mount.querySelector('.pagination-range');
            expect(range.textContent).toBe('51–100 of 100');
        });

        test('rows per page selector updates table', () => {
            const select = mount.querySelector('.rows-per-page select');
            select.value = '100';
            select.dispatchEvent(new Event('change'));
            
            expect(spannerTable.rowsPerPage).toBe(100);
            expect(spannerTable.currentPage).toBe(0);
            
            const tableRows = mount.querySelectorAll('table tr');
            // +1 for header row
            expect(tableRows.length).toBe(100 + 1);
        });
    });
});
