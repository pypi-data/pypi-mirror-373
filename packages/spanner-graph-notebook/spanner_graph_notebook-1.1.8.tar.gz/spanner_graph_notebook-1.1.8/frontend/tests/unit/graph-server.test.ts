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

import path from "path";
import fs from "fs";

// @ts-ignore
import GraphServer from '../../src/graph-server';
// @ts-ignore
import GraphNode from '../../src/models/node';

describe('GraphServer', () => {
    let graphServer: typeof GraphServer;
    const mockFetch = jest.fn();
    global.fetch = mockFetch;

    beforeEach(() => {
        mockFetch.mockClear();
        graphServer = new GraphServer(8000, JSON.stringify({
            'project': 'test-project',
            'instance': 'test-instance',
            'database': 'test-database',
            'graph': 'test-graph',
            'mock': false
        }));
    });

    describe('constructor', () => {
        it('should initialize with the default variables', () => {
            expect(graphServer.port).toBe(8000);
            expect(graphServer.params).toBe(JSON.stringify({
                'project': 'test-project',
                'instance': 'test-instance',
                'database': 'test-database',
                'graph': 'test-graph',
                'mock': false
            }));
        });

        it('should fail to initialize when no port is provided', () => {
            console.error = jest.fn();

            const defaultServer = new GraphServer(
                null,
                {}
            );

            expect(console.error).toHaveBeenCalledWith('Graph Server was not given a numerical port', {port: null});
        });

        it('should cast a string port to a number', () => {
            const server = new GraphServer(
                '1234',
                {}
            );

            expect(server.port).toBe(1234);
        });

        it('should set params values', () => {
            const params = JSON.parse(graphServer.params);
            expect(params.project).toBe('test-project');
            expect(params.instance).toBe('test-instance');
            expect(params.database).toBe('test-database');
            expect(params.graph).toBe('test-graph');
            expect(params.mock).toBe(false);
        });
    });

    describe('buildRoute', () => {
        it('should correctly build route with endpoint', () => {
            const route = graphServer.buildRoute('/test-endpoint');
            expect(route).toBe('http://localhost:8000/test-endpoint');
        });

        it('should build a route to accomodate Vertex AI', () => {
            const originalLocation = window.location;
            // @ts-ignore
            delete window.location;
            // @ts-ignore
            window.location = {...originalLocation, hostname: 'vertex-ai-workbench'};
            const route = graphServer.buildRoute('/test-endpoint');
            expect(route).toBe('/proxy/8000/test-endpoint');

            // @ts-ignore
            window.location = originalLocation;
        });
    });

    describe('node expansion', () => {
        const mockDataPath = path.join(__dirname, '../mock-data.json');
        const mockData = JSON.parse(fs.readFileSync(mockDataPath, 'utf8'));
        let mockNode: typeof GraphNode;

        beforeEach(() => {
            mockFetch.mockImplementation(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                })
            );

            mockNode = new GraphNode({
                identifier: 'test-id',
                labels: ['TestLabel'],
                key_property_names: ['test_key'],
                properties: {
                    test_key: 'test-value'
                }
            });
        });

        it('should make POST request with the correct parameters', async () => {
            const graphNode = new GraphNode({
                identifier: 'node1',
                labels: ['TestLabel1'],
                key_property_names: ['name'],
                properties: {
                    name: 'my-node-name'
                }
            });

            await graphServer.nodeExpansion(
                graphNode, 
                'OUTGOING', 
                undefined, 
                [{
                    key: 'name',
                    value: 'my-node-name',
                    type: 'STRING'
                }]
            );

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:8000/post_node_expansion',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        params: JSON.stringify({
                            project: 'test-project',
                            instance: 'test-instance',
                            database: 'test-database',
                            graph: 'test-graph',
                            mock: false
                        }),
                        request: {
                            uid: 'node1',
                            node_labels: ['TestLabel1'],
                            node_properties: [{
                                key: 'name',
                                value: 'my-node-name',
                                type: 'STRING'
                            }],
                            direction: 'OUTGOING'
                        }
                    })
                }
            );
        });

        it('should accept valid property types', async () => {
            const validTypes = ['INT64', 'STRING', 'FLOAT64', 'TIMESTAMP', 'BYTES', 'DATE', 'ENUM', 'NUMERIC', 'FLOAT32'];
            
            for (const type of validTypes) {
                await expect(graphServer.nodeExpansion(
                    mockNode, 
                    'OUTGOING', 
                    undefined, 
                    [{
                        key: 'test_key',
                        value: 'test-value',
                        type: type
                    }]
                )).resolves.toBeDefined();
            }
        });

        it('should accept lowercase valid property types', async () => {
            const validTypes = ['int64', 'string', 'float64', 'timestamp', 'bytes', 'date', 'numeric', 'float32'];
            
            for (const type of validTypes) {
                const property = {
                    key: 'test_key',
                    value: 'test_value',
                    type
                };

                await graphServer.nodeExpansion(
                    mockNode,
                    'OUTGOING',
                    undefined,
                    [property]
                );

                expect(mockFetch).toHaveBeenCalledWith(
                    expect.any(String),
                    expect.objectContaining({
                        body: expect.stringContaining(`"node_properties":[${JSON.stringify(property)}]`)
                    })
                );
                mockFetch.mockClear();
            }
        });

        it('should silently skip invalid property types', async () => {
            const invalidTypes = [
                'TYPE_CODE_UNSPECIFIED',
                'ARRAY',
                'ENUM',
                'STRUCT',
                'JSON',
                'PROTO',
                null,
                undefined,
                [],
                {},
                12345,
                'foo'
            ];

            for (const type of invalidTypes) {
                await graphServer.nodeExpansion(
                    mockNode, 
                    'OUTGOING', 
                    undefined, 
                    [{
                        key: 'test-key',
                        value: 'test-value',
                        type: type
                    }]
                );
                
                expect(mockFetch).toHaveBeenCalledWith(
                    expect.any(String),
                    expect.objectContaining({
                        body: expect.stringContaining('"node_properties":[]')
                    })
                );
                mockFetch.mockClear();
            }
        });
    });

    describe('query', () => {
        const mockDataPath = path.join(__dirname, '../mock-data.json');
        const mockData = JSON.parse(fs.readFileSync(mockDataPath, 'utf8'));

        beforeEach(() => {
            mockFetch.mockImplementation(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                })
            );
        });

        it('should make POST request with correct parameters', async () => {
            const queryString = 'SELECT * FROM test';
            await graphServer.query(queryString);

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:8000/post_query',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        query: queryString,
                        params: graphServer.params
                    })
                }
            );
        });

        it('should parse the response', async () => {
            const queryString = 'SELECT * FROM test';
            const response = await graphServer.query(queryString);

            expect(response).toEqual(mockData);
        });

        it('should handle network errors', async () => {
            const errorMessage = 'Network error';
            mockFetch.mockImplementation(() => Promise.reject(new Error(errorMessage)));
            console.error = jest.fn();

            await graphServer.query('SELECT * FROM test');
            expect(console.error).toHaveBeenCalled();
        });

        it('should handle non-ok response', async () => {
            mockFetch.mockImplementation(() =>
                Promise.resolve({
                    ok: false
                })
            );
            console.error = jest.fn();

            await graphServer.query('SELECT * FROM test');
            expect(console.error).toHaveBeenCalled();
        });

        it('should set isFetching flag during request', async () => {
            const queryPromise = graphServer.query('SELECT * FROM test');
            expect(graphServer.isFetching).toBe(true);
            await queryPromise;
            expect(graphServer.isFetching).toBe(false);
        });

        it('should handle Colab environment', async () => {
            // @ts-ignore
            global.google = {
                colab: {
                    kernel: {
                        invokeFunction: jest.fn().mockResolvedValue({
                            data: {
                                'application/json': {data: 'test-response'}
                            }
                        })
                    }
                }
            };

            const result = await graphServer.query('SELECT * FROM test');
            expect(result).toEqual({data: 'test-response'});
            // @ts-ignore
            delete global.google;
        });
    });

    describe('ping', () => {
        beforeEach(() => {
            mockFetch.mockImplementation(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({status: 'ok'})
                })
            );
            console.log = jest.fn();
        });

        it('should make GET request to ping endpoint', async () => {
            await graphServer.ping();
            expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/get_ping');
        });
    });
});