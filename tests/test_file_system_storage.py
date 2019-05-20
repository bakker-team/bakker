import filecmp
import os
import tempfile
import unittest

from pyback.sync import FileSystemStorage, retrieve, store
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

            store(self.TEST_RESOURCES_PATH, storage, checkpoint)

            remote_file_checksums = os.listdir(os.path.join(temp_path, FileSystemStorage.FILE_DIR))
            file_checksums = list(dfs_file_checksums(self.TEST_RESOURCES_PATH))

        self.assertCountEqual(remote_file_checksums, file_checksums)

    def test_retrieve(self):
        tmp_store_dir = tempfile.TemporaryDirectory()
        tmp_store_path = tmp_store_dir.name

        tmp_retrieve_dir = tempfile.TemporaryDirectory()
        tmp_retrieve_path = tmp_retrieve_dir.name

        storage = FileSystemStorage(tmp_store_path)
        checkpoint = Checkpoint.build_checkpoint(self.TEST_RESOURCES_PATH)
        store(self.TEST_RESOURCES_PATH, storage, checkpoint)

        checkpoint_id = storage.retrieve_checkpoint_ids()[0]
        retrieve(storage, checkpoint_id, tmp_retrieve_path)

        dir_comparison = filecmp.dircmp(self.TEST_RESOURCES_PATH, tmp_retrieve_path)
        self.assertEqual(dir_comparison.diff_files, [])

        # remove tmp directories after test
        tmp_store_dir.cleanup()
        tmp_retrieve_dir.cleanup()
