from os import path
import unittest

from pyback.tree import Tree


class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.CURRENT_DIR = path.dirname(path.abspath(__file__))

    def test_tree_building(self):
        tree = Tree.build_tree(path.join(
            self.CURRENT_DIR,
            '../resources/tests/backup_indexing_test_folder'))
        expected_children_count = 6
        self.assertEqual(expected_children_count, len(tree.root.children))

