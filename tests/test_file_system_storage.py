import filecmp
import os
import stat
import tempfile
import unittest

from pyback.storage import FileSystemStorage
from pyback.checkpoint import Checkpoint
from pyback.utils import get_file_digest, get_symlink_digest


class TestFileSystemStorage(unittest.TestCase):
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    TEST_RESOURCES_PATH = os.path.join(CURR_DIR, '../resources/tests/backup_indexing_test_folder')

    def test_store(self):
        def dfs_file_checksums(path):
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                assert os.path.isdir(file_path) or os.path.isfile(file_path)

                if os.path.isdir(file_path):
                    yield from dfs_file_checksums(file_path)
                elif os.path.islink(file_path):
                    yield get_symlink_digest(file_path)
                elif os.path.isfile(file_path):
                    yield get_file_digest(file_path)

        checkpoint = Checkpoint.build_checkpoint(self.TEST_RESOURCES_PATH)

        with tempfile.TemporaryDirectory() as temp_path:
            storage = FileSystemStorage(temp_path)

            storage.store(self.TEST_RESOURCES_PATH, checkpoint)

            remote_file_checksums = os.listdir(os.path.join(temp_path, FileSystemStorage.FILE_DIR))
            file_checksums = list(dfs_file_checksums(self.TEST_RESOURCES_PATH))

        self.assertCountEqual(remote_file_checksums, file_checksums)

    def test_retrieve(self):
        tmp_store_dir = tempfile.TemporaryDirectory()
        tmp_store_path = tmp_store_dir.name

        tmp_retrieve_dir_a = tempfile.TemporaryDirectory()
        tmp_retrieve_dir_b = tempfile.TemporaryDirectory()
        tmp_retrieve_dir_c = tempfile.TemporaryDirectory()
        tmp_retrieve_path_a = tmp_retrieve_dir_a.name
        tmp_retrieve_path_b = tmp_retrieve_dir_b.name
        tmp_retrieve_path_c = tmp_retrieve_dir_c.name

        storage = FileSystemStorage(tmp_store_path)
        checkpoint = Checkpoint.build_checkpoint(self.TEST_RESOURCES_PATH, 'checkpoint_name')
        storage.store(self.TEST_RESOURCES_PATH, checkpoint)

        checkpoint_meta = storage.retrieve_checkpoint_metas()[0]

        storage.retrieve(tmp_retrieve_path_a, checkpoint_meta)
        storage.retrieve_by_checksum(tmp_retrieve_path_b, checkpoint_meta.checksum[:5])
        storage.retrieve_by_name(tmp_retrieve_path_c, checkpoint_meta.name)

        dir_comparison_a = filecmp.dircmp(self.TEST_RESOURCES_PATH, tmp_retrieve_path_a)
        dir_comparison_b = filecmp.dircmp(self.TEST_RESOURCES_PATH, tmp_retrieve_path_b)
        dir_comparison_c = filecmp.dircmp(self.TEST_RESOURCES_PATH, tmp_retrieve_path_c)

        self.assertEqual(dir_comparison_a.diff_files, [])
        self.assertEqual(dir_comparison_b.diff_files, [])
        self.assertEqual(dir_comparison_c.diff_files, [])

        for dir_path, dir_names, filenames in os.walk(self.TEST_RESOURCES_PATH, followlinks=False):
            rel_path = os.path.relpath(dir_path, self.TEST_RESOURCES_PATH)

            for f in filenames:
                original_path = os.path.join(self.TEST_RESOURCES_PATH, rel_path, f)
                retrieve_path = os.path.join(tmp_retrieve_path_a, rel_path, f)
                file_permissions_origin = stat.S_IMODE(os.lstat(original_path).st_mode)
                file_permissions_restored = stat.S_IMODE(os.lstat(retrieve_path).st_mode)
                self.assertEqual(file_permissions_origin, file_permissions_restored)

        # remove tmp directories after test
        tmp_store_dir.cleanup()

        tmp_retrieve_dir_a.cleanup()
        tmp_retrieve_dir_b.cleanup()
        tmp_retrieve_dir_c.cleanup()
