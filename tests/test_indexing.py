from pyback.tree import Tree 
import unittest
from os import path

class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.CURR_DIR = path.dirname(path.abspath(__file__))

    def test_tree_building(self):
        tree = Tree.build_tree(path.join(self.CURR_DIR, 'resources/backup_indexing_test_folder'))
        root = tree.root
        expected_childs_count = 6 
        self.assertEqual(expected_childs_count, len(root.children))

if __name__ == '__main__':
    unittest.main()   



