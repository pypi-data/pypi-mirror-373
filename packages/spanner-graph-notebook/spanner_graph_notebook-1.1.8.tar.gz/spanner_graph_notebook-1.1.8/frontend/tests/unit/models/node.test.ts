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
import GraphNode from '../../../src/models/node.js';

describe('Node', () => {
    const validNodeData = {
        labels: ['Test Node'],
        properties: {
            name: 'Node Name',
            type: 'example'
        },
        key_property_names: ['name', 'type'],
        identifier: '1',
    };

    it('should create a valid node with required parameters', () => {
        const graphNode = new GraphNode(validNodeData);
        expect(graphNode).toBeDefined();
        expect(graphNode.uid).toEqual('1');
        expect(graphNode.labels).toEqual(['Test Node']);
        expect(graphNode.instantiated).toBe(true);
    });

    describe('Identifiers', () => {
        it('should parse identifiers from properties using key_property_names', () => {
            const graphNode = new GraphNode(validNodeData);
            expect(graphNode.identifiers).toEqual(['Node Name', 'example']);
        });

        it('should handle property names that fail truthiness checks', () => {
            const nodeWithFalsyPropertyName = {
                labels: ['Test Node'],
                properties: {
                    '0': 'foo',
                    'false': 'boolean',
                    '0.0': 'zero'
                },
                key_property_names: ['0', 'false', '0.0'],
                identifier: '2',
            };
            
            const graphNode = new GraphNode(nodeWithFalsyPropertyName);
            expect(graphNode.identifiers).toEqual(['foo', 'boolean', 'zero']);
        });
    });

    describe('Intermediate Nodes', () => {
        it('should create a non-intermediate node by default', () => {
            const graphNode = new GraphNode(validNodeData);
            expect(graphNode.intermediate).toBe(false);
            expect(graphNode.isIntermediateNode()).toBe(false);
        });

        it('should create an intermediate node when specified', () => {
            const intermediateNodeData = {
                ...validNodeData,
                intermediate: true
            };
            const graphNode = new GraphNode(intermediateNodeData);
            expect(graphNode.intermediate).toBe(true);
            expect(graphNode.isIntermediateNode()).toBe(true);
        });

        it('should handle undefined intermediate flag', () => {
            const nodeData = {
                ...validNodeData,
                intermediate: undefined
            };
            const graphNode = new GraphNode(nodeData);
            expect(graphNode.intermediate).toBe(false);
            expect(graphNode.isIntermediateNode()).toBe(false);
        });
    });
});