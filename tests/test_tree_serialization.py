import os
import unittest

from pyback.checkpoint import Checkpoint, DirectoryNode


class TestTreeSerialization(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_resources_dir = os.path.join(current_dir, '../resources/tests')
        
        self.tree = Checkpoint.build_checkpoint(test_resources_dir)
    
    def test_serialization(self):
        tree_json = self.tree.to_json()
        self.assertIsInstance(tree_json, str)

    def test_deserialization(self):
        new_tree = Checkpoint.from_json(self.tree.to_json())
        self.assertIsInstance(new_tree, Checkpoint)

    def test_serialized_structure(self):
        new_tree = Checkpoint.from_json(self.tree.to_json())
        self.check_tree_nodes(self.tree.root, new_tree.root)
        
    def check_tree_nodes(self, tree_node_a, tree_node_b):
        self.assertEqual(tree_node_a.name, tree_node_b.name)
        self.assertEqual(tree_node_a.__class__, tree_node_b.__class__)

        if isinstance(tree_node_a, DirectoryNode):
            for name, child_node_a in tree_node_a.children.items():
                child_node_b = tree_node_b.children[name]
                self.check_tree_nodes(child_node_a, child_node_b)

