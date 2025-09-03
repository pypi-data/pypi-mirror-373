# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides test for the graph_entities implementation"""

import unittest
import networkx as nx
from spanner_graphs.graph_entities import Node, Edge


class TestNode(unittest.TestCase):
    """Test case for a Node"""

    def test_node_creation(self):
        """Test that a node is created correctly using `Node.from_json`"""
        data = {
            "identifier": "1",
            "labels": ["Person"],
            "properties": {
                "name": "Emmanuel"
            },
        }

        node = Node.from_json(data)
        self.assertEqual(node.identifier, "1")
        self.assertEqual(node.labels, ["Person"])
        self.assertEqual(node.properties, {"name": "Emmanuel"})
        self.assertFalse(node.intermediate, "Node should not be intermediate by default")

    def test_intermediate_flag_in_constructor(self):
        """Test that the intermediate flag is set correctly in the constructor"""
        # Test with intermediate=True
        node1 = Node("1", ["Person"], {"name": "Emmanuel"}, intermediate=True)
        self.assertTrue(node1.intermediate, "Node should be marked as intermediate")

        # Test with intermediate=False
        node2 = Node("2", ["Person"], {"name": "John"}, intermediate=False)
        self.assertFalse(node2.intermediate, "Node should not be marked as intermediate")

        # Test with default (should be False)
        node3 = Node("3", ["Person"], {"name": "Alice"})
        self.assertFalse(node3.intermediate, "Node should default to not intermediate")

    def test_make_intermediate(self):
        """Test the make_intermediate static method"""
        test_identifier = "test123"
        node = Node.make_intermediate(test_identifier)

        self.assertEqual(node.identifier, test_identifier, "Identifier should match input")
        self.assertEqual(node.labels, ["Intermediate"], "Labels should include 'Intermediate'")
        self.assertTrue(node.intermediate, "Node should be marked as intermediate")
        self.assertIn("note", node.properties, "Properties should include a note field")
        self.assertTrue(
            "referenced entity" in node.properties["note"],
            "Note should explain this is a referenced entity"
        )

    def test_to_json_with_intermediate(self):
        """Test that to_json correctly includes the intermediate flag"""
        # Test with intermediate=True
        node1 = Node("1", ["Person"], {"name": "Jill"}, intermediate=True)
        json1 = node1.to_json()
        self.assertTrue(json1["intermediate"], "JSON should include intermediate=True")

        # Test with intermediate=False
        node2 = Node("2", ["Person"], {"name": "John"}, intermediate=False)
        json2 = node2.to_json()
        self.assertFalse(json2["intermediate"], "JSON should include intermediate=False")

class TestEdge(unittest.TestCase):
    """Test cases for the Edge class"""

    def test_edge_creation(self):
        """Test that an Edge object is created correctly"""
        data = {
            "identifier": "3",
            "source_node_identifier": "1",
            "destination_node_identifier": "2",
            "labels": ["KNOWS"],
            "properties": {
                "since": "2020"
            },
        }

        edge = Edge.from_json(data)
        self.assertEqual(edge.source, "1")
        self.assertEqual(edge.destination, "2")
        self.assertEqual(edge.labels, ["KNOWS"])
        self.assertEqual(edge.properties, {"since": "2020"})

    def test_add_edge_to_graph(self):
        """Test that an edge is added correct to a graph"""
        graph = nx.DiGraph()
        node_mapping = {"1": 1, "2": 2}

        data = {
            "identifier": "1",
            "source_node_identifier": "1",
            "destination_node_identifier": "2",
            "labels": ["KNOWS"],
            "properties": {
                "since": "2020"
            },
        }

        edge = Edge.from_json(data)
        edge.add_to_graph(graph)

        self.assertIn(('1', '2'), graph.edges)
        # self.assertEqual(graph.edges[1, 2]["label"], "KNOWS")
        # self.assertEqual(graph.edges[1, 2]["title"],
        #                  "--- Edge Properties ---\nsince: 2020")

    def test_add_edge_to_graph_with_missing_nodes(self):
        """Test that edge with a missing node is not added to graph"""
        graph = nx.DiGraph()
        node_mapping = {"1": 1}

        data = {
            "identifier": "2",
            "source_node_identifier": "1",
            "destination_node_identifier": "2",
            "labels": ["KNOWS"],
            "properties": {
                "since": "2020"
            },
        }

        edge = Edge.from_json(data)
        edge.add_to_graph(graph)

        self.assertNotIn((1, 2), graph.edges)
