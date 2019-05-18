import os
import unittest

from pyback.tree import Tree


class TestTreeSerialization(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_resources_dir = os.path.join(current_dir, '../resources/tests')
        
        self.tree = Tree.build_tree(test_resources_dir)
    
    def test_serialization(self):
        tree_json = self.tree.to_json()
        self.assertIsInstance(tree_json, str)

    def test_deserialization(self):
        new_tree = Tree.from_json(self.tree.to_json(), '')
        self.assertIsInstance(new_tree, Tree)

    def test_serialized_structure(self):
        new_tree = Tree.from_json(self.tree.to_json(), '')
        self.check_tree_nodes(self.tree.root, new_tree.root)
        
    def check_tree_nodes(self, tree_node_a, tree_node_b):
        self.assertEqual(tree_node_a.name, tree_node_b.name)
        self.assertEqual(tree_node_a.is_file, tree_node_b.is_file)
        # check all children
        for name, child_node_a in tree_node_a.children.items():
            child_node_b = tree_node_b.children[name]
            self.check_tree_nodes(child_node_a, child_node_b)

