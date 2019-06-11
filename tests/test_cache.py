import importlib
import os
import tempfile
import unittest

from bakker.checkpoint import Checkpoint
from bakker.cache import Cache
from tests import utils


class TestCache(unittest.TestCase):
    def setUp(self):
        self.resources_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../resources/tests/backup_indexing_test_folder')

    def test_cache_write(self):
        cache = Cache.build_cache(self.resources_path)

        file_path = os.path.join(self.resources_path, '100000_lines.md')
        file_checksum = utils.digest(file_path)
        self.assertEqual(cache.get_file_path(file_checksum), file_path)

        symlink_path = os.path.join(self.resources_path, '100000_lines_symlink')
        symlink_checksum = utils.digest(symlink_path)
        self.assertEqual(cache.get_file_path(symlink_checksum), symlink_path)

        nested_file_path = os.path.join(self.resources_path, 'folder1/folder3/folder8/hello-2.10.tar.gz')
        nested_file_checksum = utils.digest(nested_file_path)
        self.assertEqual(cache.get_file_path(nested_file_checksum), nested_file_path)

    def test_cache_move(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            cache = Cache.build_cache(self.resources_path)

            file_path = os.path.join(self.resources_path, '100000_lines.md')
            file_checksum = utils.digest(file_path)
            new_file_path = os.path.join(tmp_path, 'filename.md')
            cache.set_file_path(file_checksum, new_file_path)
            self.assertEqual(cache.get_file_path(file_checksum), new_file_path)
            self.assertEqual(cache.is_file_moved(file_checksum), True)

            symlink_path = os.path.join(self.resources_path, '100000_lines_symlink')
            symlink_checksum = utils.digest(symlink_path)
            new_symlink_path = os.path.join(tmp_path, 'symlink')
            cache.set_file_path(symlink_checksum, new_symlink_path)
            self.assertEqual(cache.get_file_path(symlink_checksum), new_symlink_path)
            self.assertEqual(cache.is_file_moved(symlink_checksum), True)


