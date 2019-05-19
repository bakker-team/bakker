from os import path
import unittest

from pyback.checkpoint import Checkpoint


class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.indexing_folder = path.join(
                path.dirname(path.abspath(__file__)),
                '../resources/tests/backup_indexing_test_folder'
                )

    def test_tree_building(self):
        tree = Checkpoint.build_checkpoint(self.indexing_folder)
                
        expected_children_count = 6
        self.assertEqual(expected_children_count, len(tree.root.children))

    def test_file_permission(self):
        # Windows / Linux Subsystem on Windows cannot handle this test correctly and therefore needs to be excluded.
        import platform
        if platform.system() == 'Windows':
            return
        if 'Microsoft' in platform.release():
            return

        file_path = path.join(self.indexing_folder, '100000_lines.md')
        symlink_path = path.join(self.indexing_folder, '100000_lines_symlink')

        file_permissions = 0o644
        symlink_permissions = 0o777

        tree = Checkpoint.build_checkpoint(self.indexing_folder)

        self.assertEqual(tree.root.children['100000_lines.md'].permissions, file_permissions)
        self.assertEqual(tree.root.children['100000_lines_symlink'].permissions, symlink_permissions)

