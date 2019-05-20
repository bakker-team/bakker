from os import path
import unittest

from pyback.checkpoint import Checkpoint


class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.indexing_folder = path.join(
                path.dirname(path.abspath(__file__)),
                '../resources/tests/backup_indexing_test_folder'
                )
    # TODO extend the test to verify that a correct checkpoint is built.
    def test_checkpoint_building(self):
        checkpoint = Checkpoint.build_checkpoint(self.indexing_folder)
                
        expected_children_count = 6
        self.assertEqual(expected_children_count, len(checkpoint.root.children))

    def test_file_permission(self):
        # Windows / Linux Subsystem on Windows cannot handle this test correctly and therefore needs to be excluded.
        import platform
        if platform.system() == 'Windows':
            return
        if 'Microsoft' in platform.release():
            return

        file = '100000_lines.md'
        file_permissions = 0o644

        symlink = '100000_lines_symlink'
        symlink_permissions = 0o777

        checkpoint = Checkpoint.build_checkpoint(self.indexing_folder)

        self.assertEqual(checkpoint.root.children[file].permissions, file_permissions)
        self.assertEqual(checkpoint.root.children[symlink].permissions, symlink_permissions)

