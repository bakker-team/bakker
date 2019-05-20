import os
import tempfile
import unittest

from pyback.sync import FileSystemStorage, retrieve, store
from pyback.checkpoint import Checkpoint
from pyback.utils import get_file_digest, get_symlink_digest


class TestFileSystemStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        self.storage = FileSystemStorage(self.temp_path)

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

        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_resources_path = os.path.join(current_dir, '../resources/tests/backup_indexing_test_folder')
        
        checkpoint = Checkpoint.build_checkpoint(test_resources_path)
        store(test_resources_path, self.storage, checkpoint)

        remote_file_checksums = os.listdir(os.path.join(self.temp_path, FileSystemStorage.FILE_DIR))
        file_checksums = list(dfs_file_checksums(test_resources_path))

        self.assertCountEqual(remote_file_checksums, file_checksums)


    def test_retrieve(self):
        pass


    def tearDown(self):
        self.temp_dir.cleanup()
