/**
 * Copyright 2024 Google LLC
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
 */


/**
 * SpannerTable - A class to render a table view of graph data.
 */
class SpannerTable {
    svg = {
        up: `<svg height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368"><path d="M480-528 296-344l-56-56 240-240 240 240-56 56-184-184Z"/></svg>`,
        down: `<svg height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368"><path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/></svg>`
    };

    /**
     * @type {HTMLElement}
     */
    mount = null;
    /**
     * @type {HTMLElement}
     */
    menuMount = null;

    /**
     * @type {GraphStore}
     */
    store = null;

    /**
     * [
     *     [{column_1_data}, {column_2_data}, {column_3_data}, ...],
     *     [{column_1_data}, {column_2_data}, {column_3_data}, ...],
     *     ...
     * ]
     * @type {Array<Array<Object>>}
     */
    rows = [];

    currentPage = 0;
    rowsPerPage = 0;
    pageLengths = [50, 100, 200]

    /**
     * Creates an instance of SpannerTable.
     * @param {GraphStore} store
     * @param {HTMLElement} mount
     * @param {HTMLElement} menuMount
     */
    constructor(store, mount, menuMount) {
        this.store = store;
        this.mount = mount;
        this.menuMount = menuMount;
        this.currentPage = 0;
        this.rowsPerPage = this.pageLengths[0];
        this.expandedRows = new Set(); // Track expanded rows

        this.initializeEvents();
        this.parseQueryResultToRows();
        this.render();
    }

    initializeEvents() {
        const debounce = (callback, timeout = 300) => {
            let timer = 0;
            return (...args) => {
                window.clearTimeout(timer);
                timer = window.setTimeout(() => {
                    callback.apply(this, args);
                }, timeout);
            }
        }

        const fullscreenMount = this.mount.parentElement.parentElement;
        window.addEventListener('fullscreenchange', debounce((e) => {
            if (fullscreenMount !== e.target) {
                return;
            }

            if (!document.fullscreenElement) {
                this.mount.style.width = '100%';
                this.mount.style.height = '616px';
            } else {
                const height = window.innerHeight - this.menuMount.offsetHeight;
                this.mount.style.width = window.innerWidth + 'px';
                this.mount.style.height = height + 'px';
            }
        }));
    }

    /**
     * Prepare query result data to be rendered in the table.
     *
     * queryResult is formatted as such:
     * {
     *     field_string_A: [{data_1}, {data_2}, {data_3}]
     *     field_string_B: [{data_1}, {data_2}, {data_3}]
     * }
     * We want it transformed to an array of rows that matches
     * the presentation of the table:
     * [
     *     // field A   field B   field C
     *     [{data_1},  {data_1}, {data_1}]
     *     [{data_2},  {data_2}, {data_2}]
     *     [{data_3},  {data_3}, {data_3}]
     * ]
     */
    parseQueryResultToRows() {
        if (!this.store || !this.store.config) {
            this.handleError('Cannot generate table: sorry, something went wrong');
            return;
        }

        if (!this.store.config.queryResult || typeof this.store.config.queryResult !== 'object') {
            this.handleError('Cannot generate table: query result not found or malformed');
            console.error('Cannot generate table: query result not found or malformed', this.store.config.queryResult);
            return;
        }

        try {
            this.rows = [];

            const fields = Object.keys(this.store.config.queryResult);

            const rowCount = fields.reduce((max, field) => {
                const rows = this.store.config.queryResult[field];
                return rows instanceof Array ? Math.max(max, rows.length) : max;
            }, 0);

            for (let i = 0; i < rowCount; i++) {
                const row = [];
                for (const field of fields) {
                    if (i < this.store.config.queryResult[field].length) {
                        row.push(this.store.config.queryResult[field][i]);
                    } else {
                        row.push({})
                    }
                }
                this.rows.push(row);
            }
        } catch (error) {
            this.handleError('Cannot generate table: sorry, something went wrong');
            console.error('Error generating table:', error);
        }
    }

    render() {
        if (!this.store || !this.store.config) {
            this.handleError('Cannot generate table: sorry, something went wrong');
            return;
        }

        if (!this.store.config.queryResult || typeof this.store.config.queryResult !== 'object') {
            this.handleError('Cannot generate table: query result not found or malformed');
            console.error('Cannot generate table: query result not found or malformed', this.store.config.queryResult);
            return;
        }

        this.mount.innerHTML = `
            <style>
                /* Add styles for the container itself */
                #${this.mount.id} {
                    width: 100%;
                    max-width: 100%;
                    height: 616px;
                    overflow: scroll;
                    display: flex;
                    flex-direction: column;
                }
            
                #${this.mount.id} table.spanner-table {
                    table-layout: fixed !important;
                    border-collapse: collapse;
                    font-family: 'Google Sans', Roboto, Arial, sans-serif;
                    width: max-content;
                    min-width: 100%;
                    margin-bottom: 0;
                }
                
                .table-error {
                    padding: 2rem;
                    color: #d93025;
                    background: #fce8e6;
                    border-radius: 4px;
                    margin: 1rem;
                    font-family: 'Google Sans', Roboto, Arial, sans-serif;
                }
                
                .table-empty-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 3rem;
                    color: #5f6368;
                }
            
                .spanner-table-wrapper {
                    overflow-x: auto;
                    width: 100%;
                    position: relative;
                    max-width: 100%;
                    display: block;
                    overflow-y: scroll;
                    flex: 1;
                    background-color: #FBFDFF;
                }
            
                .spanner-table th, .spanner-table td {
                    border-bottom: 1px solid #ddd;
                    text-align: left;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    vertical-align: middle;
                    padding: 0 0 0 8px;
                }
            
                .spanner-table th {
                    background-color: #f2f2f2;
                    position: sticky;
                    top: 0;
                    font-weight: 500;
                    color: rgb(112, 112, 112);
                    text-align: left !important;
                    z-index: 9;
                }
            
                div.spanner-table-wrapper table.spanner-table tbody tr {
                    background-color: #fff;
                }
                
                div.spanner-table-wrapper table.spanner-table tr {
                    height: 1.75rem;
                    padding: 0;
                }
            
                div.spanner-table-wrapper table.spanner-table tbody tr:hover {
                    background-color: #f5f5f5;
                }
                
                table.spanner-table thead tr th.expand-column.header, 
                table.spanner-table tbody tr td.expand-column {
                    padding: 0 !important;
                    box-sizing: content-box !important;
                    min-width: 32px !important;
                    max-width: 32px !important;
                    width: 32px !important;
                }
            
                table.spanner-table tbody tr td.expand-column {
                    position: sticky;
                    right: -1px;
                    background: white;
                    text-align: center;
                    z-index: 1;
                    vertical-align: top !important;
                }
            
                table.spanner-table tbody tr td.expand-column::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    border-left: 1px solid #ddd;
                }
            
                .expand-icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                
                    cursor: pointer;
                    opacity: 0.7;
                    line-height: 0;
                    height: 1.75rem;
                    
                }
            
                .expand-icon:hover {
                    opacity: 1;
                }
            
                .cell-content {
                    overflow: hidden;
                    text-overflow: ellipsis;
                    text-align: left;
                    line-height: 1.2rem;
                    font-size: .8rem;
                }
            
                .expanded .cell-content {
                    overflow: visible;
                    white-space: pre-wrap;
                    max-height: none;
                    word-break: break-word;
                }
            
                .expanded td {
                    white-space: normal;
                    max-height: none;
                    overflow: visible;
                }
            
                .pagination-controls {
                    display: flex;
                    justify-content: flex-end;
                    align-items: center;
                    padding: 16px;
                    color: rgb(112, 112, 112);
                    font-size: 14px;
                    border-top: 1px solid #ddd;
                }
            
                .rows-per-page {
                    margin-right: 32px;
                }
            
                .rows-per-page select {
                    margin: 0 8px;
                    padding: 4px;
                }
            
                .pagination-range {
                    margin-right: 32px;
                }
            
                .pagination-arrows {
                    display: flex;
                    gap: 8px;
                }
            
                .pagination-arrow {
                    cursor: pointer;
                    padding: 4px;
                    opacity: 0.7;
                    background-color: #fff;
                    border: none;
                }
            
                .pagination-arrow:hover {
                    opacity: 1;
                }
            
                .pagination-arrow[disabled] {
                    opacity: 0.3;
                    cursor: default;
                }
            
                td {
                    position: relative;
                }
            </style>
            <div class="spanner-table-wrapper">
                <div class="table-error hidden"></div>
                <div class="table-empty-state hidden">
                    <p>No data available to display</p>
                </div>
                <table class="spanner-table"></table>
            </div>
        `;

        if (this.rows.length === 0) {
            this.mount.querySelector('.table-empty-state').classList.remove('hidden');
            return;
        }

        const table = this.mount.querySelector('.spanner-table');

        const thead = this.createTableHeader();
        if (thead instanceof HTMLElement) {
            table.appendChild(thead);
        }

        const tbody = this.createTableBody();
        if (tbody instanceof HTMLElement) {
            table.appendChild(tbody);
        }

        this.createPaginationControls();
    }

    handleError(message, type = 'error') {
        const errorContainer = this.mount.querySelector('.table-error');
        const tableWrapper = this.mount.querySelector('.spanner-table');

        errorContainer.classList.remove('hidden');
        errorContainer.textContent = message;
        tableWrapper.classList.add('hidden');
    }

    /**
     * @returns {HTMLElement} The table header element.
     */
    createTableHeader() {
        if (!this.store || !this.store.config) {
            console.error('Cannot generate table: requires store and config');
            return null;
        }

        if (!this.store.config.queryResult || typeof this.store.config.queryResult !== 'object') {
            console.error('Cannot generate table: query result not found or malformed', this.store.config.queryResult);
            return null;
        }

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');

        Object.keys(this.store.config.queryResult).forEach(field => {
            let header = field;
            if (typeof field !== 'string') {
                console.warn('Table header error: expecting field to be a string', field);
                header = 'column';
            }

            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });

        // Add expand column header
        const expandHeader = document.createElement('th');
        expandHeader.className = 'expand-column header';
        headerRow.appendChild(expandHeader);

        thead.appendChild(headerRow);
        return thead;
    }

    /**
     * Formats cell content based on the data type and header configuration
     * @param {Object} cellData - The data to format
     * @param {number} rowIndex - The absolute index of this row
     * @returns {{truncated: boolean, content: string}} Formatted string representation
     */
    formatCellContent(cellData, rowIndex) {
        let content = '';
        let truncated = false;

        if (cellData === null || cellData === undefined || cellData === '') {
            return {content, truncated};
        }

        try {
            if (this.expandedRows.has(rowIndex)) {
                switch (typeof cellData) {
                    case 'string':
                        content = cellData;
                        break;
                    case 'object':
                        content = JSON.stringify(cellData, null, 4) || '{}';
                        break;
                    default:
                        content = String(cellData);
                }
            } else {
                switch (typeof cellData) {
                    case 'string':
                        content = cellData;
                        break;
                    case 'object':
                        content = JSON.stringify(cellData) || '{}';
                        break;
                    default:
                        content = String(cellData);
                }

                truncated = content.length > 80;
                if (truncated) {
                    content = content.substring(0, 77) + '...';
                }
            }

        } catch (error) {
            console.warn(`Error formatting cell data:`, {error, cellData, rowIndex});
            content = '<Error: check console>';
        }

        return {content, truncated};
    }

    /**
     * @returns {HTMLElement} The table body element.
     */
    createTableBody() {
        const tbody = document.createElement('tbody');
        if (!this.rows instanceof Array) {
            return tbody;
        }

        const start = this.currentPage * this.rowsPerPage;
        const end = start + this.rowsPerPage;
        const pageData = this.rows.slice(start, end);
        pageData.forEach((rowData, rowIndex) => {
            const absoluteRowIndex = start + rowIndex; // Calculate absolute row index
            const row = document.createElement('tr');
            let showExpansionArrow = false;

            rowData.forEach((cellData, index) => {
                const td = document.createElement('td');
                const contentDiv = document.createElement('div');
                contentDiv.className = 'cell-content';
                const {content, truncated} = this.formatCellContent(cellData, absoluteRowIndex);
                contentDiv.textContent = content;
                td.appendChild(contentDiv);
                row.appendChild(td);

                showExpansionArrow = showExpansionArrow || truncated;
            });

            // Add expand column
            const expandTd = document.createElement('td');
            expandTd.className = 'expand-column';
            if (showExpansionArrow) {
                const expandIcon = document.createElement('span');
                expandIcon.innerHTML = this.expandedRows.has(absoluteRowIndex) ? this.svg.down : this.svg.up;
                expandIcon.className = 'expand-icon';
                expandIcon.onclick = (e) => {
                    e.stopPropagation();
                    const isExpanded = this.expandedRows.has(absoluteRowIndex);
                    if (isExpanded) {
                        this.expandedRows.delete(absoluteRowIndex);
                        expandIcon.innerHTML = this.svg.up;
                    } else {
                        this.expandedRows.add(absoluteRowIndex);
                        expandIcon.innerHTML = this.svg.down;
                    }
                    row.classList.toggle('expanded', !isExpanded);
                    this.updateRowContent(row, rowData, absoluteRowIndex);
                };
                expandTd.appendChild(expandIcon);
            }
            row.appendChild(expandTd);

            if (this.expandedRows.has(absoluteRowIndex)) {
                row.classList.add('expanded');
            }

            tbody.appendChild(row);
        });

        return tbody;
    }

    /**
     * Updates the content of a row when expansion state changes
     * @param {HTMLElement} row - The row element to update
     * @param {Array} rowData - The data for this row
     * @param {number} rowIndex - The absolute index of this row
     */
    updateRowContent(row, rowData, rowIndex) {
        if (!(row instanceof HTMLElement)) {
            return;
        }

        const cells = Array.from(row.children).slice(0, -1); // Exclude expand column
        for (let i = 0; i < cells.length; i++) {
            const contentDiv = cells[i].querySelector('.cell-content');
            if (!contentDiv) {
                return;
            }

            contentDiv.textContent = this.formatCellContent(rowData[i], rowIndex).content;
        }
    }

    /**
     * Creates pagination controls.
     */
    createPaginationControls() {
        const pagination = document.createElement('div');
        pagination.className = 'pagination-controls';

        // Rows per page dropdown
        const rowsPerPage = document.createElement('div');
        rowsPerPage.className = 'rows-per-page';
        const select = document.createElement('select');
        this.pageLengths.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            option.selected = value === this.rowsPerPage;
            select.appendChild(option);
        });
        select.addEventListener('change', (e) => {
            this.rowsPerPage = parseInt(e.target.value);
            this.currentPage = 0; // Reset to first page when changing page size
            this.render();
        });

        rowsPerPage.appendChild(document.createTextNode('Rows per page:'));
        rowsPerPage.appendChild(select);

        // Pagination range
        const range = document.createElement('div');
        range.className = 'pagination-range';
        const start = this.currentPage * this.rowsPerPage + 1;
        const end = Math.min((this.currentPage + 1) * this.rowsPerPage, this.rows.length);
        range.textContent = `${start}–${end} of ${this.rows.length}`;

        // Pagination arrows
        const arrows = document.createElement('div');
        arrows.className = 'pagination-arrows';

        const createArrow = (text, onClick, disabled) => {
            const arrow = document.createElement('button');
            arrow.className = 'pagination-arrow';
            arrow.textContent = text;
            arrow.onclick = onClick;
            if (disabled) arrow.setAttribute('disabled', '');
            return arrow;
        };

        arrows.appendChild(createArrow('⟨⟨', () => this.goToPage(0), this.currentPage === 0));
        arrows.appendChild(createArrow('⟨', () => this.goToPage(this.currentPage - 1), this.currentPage === 0));
        arrows.appendChild(createArrow('⟩', () => this.goToPage(this.currentPage + 1), end >= this.rows.length));
        arrows.appendChild(createArrow('⟩⟩', () => this.goToPage(Math.floor(this.rows.length / this.rowsPerPage)), end >= this.rows.length));

        pagination.appendChild(rowsPerPage);
        pagination.appendChild(range);
        pagination.appendChild(arrows);
        this.mount.appendChild(pagination);
    }

    goToPage(page) {
        this.currentPage = page;
        this.render();
    }
}

export default SpannerTable;