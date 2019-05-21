import os
import stat
import unittest

from bakker.checkpoint import Checkpoint


class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.TEST_RESOURCES_PATH = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../resources/tests/backup_indexing_test_folder'
                )

    # TODO extend the test to verify that a correct checkpoint is built.
    def test_checkpoint_building(self):
        checkpoint = Checkpoint.build_checkpoint(self.TEST_RESOURCES_PATH)
                
        expected_children_count = 6
        self.assertEqual(expected_children_count, len(checkpoint.root.children))

    def test_file_permission(self):
        # Windows / Linux Subsystem on Windows cannot handle this test correctly and therefore needs to be excluded.
        import platform
        if platform.system() == 'Windows':
            return
        if 'Microsoft' in platform.release():
            return

        file_name = '100000_lines.md'
        file_path = os.path.join(self.TEST_RESOURCES_PATH, file_name)
        file_permissions = stat.S_IMODE(os.lstat(file_path).st_mode)

        symlink_name = '100000_lines_symlink'
        symlink_path = os.path.join(self.TEST_RESOURCES_PATH, symlink_name)
        symlink_permissions = stat.S_IMODE(os.lstat(symlink_path).st_mode)

        checkpoint = Checkpoint.build_checkpoint(self.TEST_RESOURCES_PATH)

        self.assertEqual(checkpoint.root.children[file_name].permissions, file_permissions)
        self.assertEqual(checkpoint.root.children[symlink_name].permissions, symlink_permissions)
