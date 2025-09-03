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
 */

// @ts-ignore
import Schema from '../../../src/models/schema.js';

describe('Schema', () => {
    const mockPropertyDeclarations = [
        { name: 'age', type: 'INT64' },
        { name: 'name', type: 'STRING' },
        { name: 'active', type: 'BOOL' }
    ];

    const mockNodeTable = {
        name: 'Users',
        labelNames: ['User'],
        propertyDefinitions: [
            { propertyDeclarationName: 'age' },
            { propertyDeclarationName: 'name' }
        ],
        keyColumns: ['id'],
        kind: 'NODE',
        baseCatalogName: 'test',
        baseSchemaName: 'test',
        baseTableName: 'users'
    };

    const mockNodeTable2 = {
        name: 'Posts',
        labelNames: ['Post'],
        propertyDefinitions: [
            { propertyDeclarationName: 'name' }
        ],
        keyColumns: ['id'],
        kind: 'NODE',
        baseCatalogName: 'test',
        baseSchemaName: 'test',
        baseTableName: 'posts'
    };

    const mockEdgeTable = {
        name: 'Follows',
        labelNames: ['FOLLOWS'],
        propertyDefinitions: [
            { propertyDeclarationName: 'active' }
        ],
        keyColumns: ['id'],
        kind: 'EDGE',
        sourceNodeTable: {
            nodeTableName: 'Users',
            edgeTableColumns: ['source_id'],
            nodeTableColumns: ['id']
        },
        destinationNodeTable: {
            nodeTableName: 'Users',
            edgeTableColumns: ['target_id'],
            nodeTableColumns: ['id']
        },
        baseCatalogName: 'test',
        baseSchemaName: 'test',
        baseTableName: 'follows'
    };

    const mockEdgeTable2 = {
        name: 'Created',
        labelNames: ['CREATED'],
        propertyDefinitions: [],
        keyColumns: ['id'],
        kind: 'EDGE',
        sourceNodeTable: {
            nodeTableName: 'Users',
            edgeTableColumns: ['user_id'],
            nodeTableColumns: ['id']
        },
        destinationNodeTable: {
            nodeTableName: 'Posts',
            edgeTableColumns: ['post_id'],
            nodeTableColumns: ['id']
        },
        baseCatalogName: 'test',
        baseSchemaName: 'test',
        baseTableName: 'created'
    };

    const mockSchemaData = {
        catalog: 'test',
        schema: 'test',
        name: 'test_schema',
        labels: 2,
        nodeTables: [mockNodeTable, mockNodeTable2],
        edgeTables: [mockEdgeTable, mockEdgeTable2],
        propertyDeclarations: mockPropertyDeclarations
    };

    describe('constructor', () => {
        it('should initialize with valid schema data', () => {
            const schema = new Schema(mockSchemaData);
            expect(schema.rawSchema).toBeDefined();
            expect(schema.rawSchema.nodeTables).toHaveLength(2);
            expect(schema.rawSchema.edgeTables).toHaveLength(2);
        });

        it('should handle invalid input gracefully', () => {
            const schema = new Schema(null);
            expect(schema.rawSchema).toBeNull();
        });

        it('should initialize empty arrays for missing data', () => {
            const schema = new Schema({});
            expect(schema.rawSchema.nodeTables).toEqual([]);
            expect(schema.rawSchema.edgeTables).toEqual([]);
            expect(schema.rawSchema.propertyDeclarations).toEqual([]);
        });
    });

    describe('table names and labels', () => {
        let schema: typeof Schema;

        beforeEach(() => {
            schema = new Schema(mockSchemaData);
        });

        it('should get node names correctly', () => {
            const nodeNames = schema.getNodeNames();
            expect(nodeNames).toContain('User');
        });

        it('should get edge names correctly', () => {
            const edgeNames = schema.getEdgeNames();
            expect(edgeNames).toContain('FOLLOWS');
        });

        it('should get all table names', () => {
            const tableNames = schema.getTableNames();
            expect(tableNames.nodes).toContain('User');
            expect(tableNames.edges).toContain('FOLLOWS');
        });

        it('should handle non-array input in getUniqueLabels', () => {
            const labels = schema.getUniqueLabels(null);
            expect(labels).toEqual([]);
        });

        it('should handle tables without labelNames', () => {
            const labels = schema.getUniqueLabels([{ name: 'Test' }]);
            expect(labels).toEqual([]);
        });

        it('should handle invalid table names', () => {
            const names = schema.getNamesOfTables([
                { name: null },
                { name: 123 },
                {}
            ]);
            expect(names).toEqual([]);
        });
    });

    describe('property handling', () => {
        let schema: typeof Schema;

        beforeEach(() => {
            schema = new Schema(mockSchemaData);
        });

        it('should get properties of a node table', () => {
            const properties = schema.getPropertiesOfTable(mockNodeTable);
            expect(properties['age']).toBe('INT64');
            expect(properties['name']).toBe('STRING');
        });

        it('should get properties of an edge table', () => {
            const properties = schema.getPropertiesOfTable(mockEdgeTable);
            expect(properties['active']).toBe('BOOL');
        });

        it('should handle missing property definitions', () => {
            const properties = schema.getPropertiesOfTable({});
            expect(Object.keys(properties)).toHaveLength(0);
        });

        it('should handle undefined property declarations', () => {
            const invalidSchema = new Schema({
                ...mockSchemaData,
                propertyDeclarations: undefined
            });
            const properties = invalidSchema.getPropertiesOfTable(mockNodeTable);
            expect(properties).toEqual({});
        });

        it('should handle property declarations without matching definitions', () => {
            const properties = schema.getPropertiesOfTable({
                propertyDefinitions: [
                    { propertyDeclarationName: 'nonexistent' }
                ]
            });
            expect(properties).toEqual({});
        });
    });

    describe('edge and node relationships', () => {
        let schema: typeof Schema;

        beforeEach(() => {
            schema = new Schema(mockSchemaData);
        });

        it('should get edges of a node', () => {
            const edges = schema.getEdgesOfNode(mockNodeTable);
            expect(edges).toHaveLength(2);
            expect(edges.map((e: { name: string }) => e.name).sort()).toEqual(['Created', 'Follows']);
        });

        it('should check if node is connected to edge', () => {
            const isConnected = schema.nodeIsConnectedToEdge('Users', 'Follows');
            expect(isConnected).toEqual({
                isConnected: true,
                isSource: true
            });
        });

        it('should get edge from name', () => {
            const edge = schema.getEdgeFromName('Follows');
            expect(edge).toBeDefined();
            expect(edge.name).toBe('Follows');
        });

        it('should get node from name', () => {
            const node = schema.getNodeFromName('Users');
            expect(node).toBeDefined();
            expect(node.name).toBe('Users');
        });

        describe('getNodesOfEdges', () => {
            it('should get source and destination nodes of an edge', () => {
                const nodes = schema.getNodesOfEdges(mockEdgeTable2);
                expect(nodes.from.name).toBe('Users');
                expect(nodes.to.name).toBe('Posts');
            });

            it('should handle edge table without matching nodes', () => {
                const invalidEdge = {
                    ...mockEdgeTable,
                    sourceNodeTable: { nodeTableName: 'NonExistent' },
                    destinationNodeTable: { nodeTableName: 'AlsoNonExistent' }
                };
                const nodes = schema.getNodesOfEdges(invalidEdge);
                expect(nodes.from).toBeUndefined();
                expect(nodes.to).toBeUndefined();
            });
        });

        it('should handle non-existent node in nodeIsConnectedToEdge', () => {
            const result = schema.nodeIsConnectedToEdge('NonExistent', 'Follows');
            expect(result).toEqual({
                isConnected: false,
                isSource: false
            });
        });

        it('should handle non-existent edge in nodeIsConnectedToEdge', () => {
            const result = schema.nodeIsConnectedToEdge('Users', 'NonExistent');
            expect(result).toEqual({
                isConnected: false,
                isSource: false
            });
        });

        it('should identify node as destination in nodeIsConnectedToEdge', () => {
            const result = schema.nodeIsConnectedToEdge('Posts', 'Created');
            expect(result).toEqual({
                isConnected: true,
                isSource: false
            });
        });
    });

    describe('table IDs and display names', () => {
        let schema: typeof Schema;

        beforeEach(() => {
            schema = new Schema(mockSchemaData);
        });

        it('should get edge table ID', () => {
            const id = schema.getEdgeTableId(mockEdgeTable);
            expect(id).toBe(0);
        });

        it('should get node table ID', () => {
            const id = schema.getNodeTableId(mockNodeTable);
            expect(id).toBe(0);
        });

        it('should get display name', () => {
            const displayName = schema.getDisplayName(mockNodeTable);
            expect(displayName).toBe('User');
        });
    });
});
