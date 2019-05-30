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
        file_digest = utils.digest(file_path)
        self.assertEqual(cache[file_digest][0], file_path)

        symlink_path = os.path.join(self.resources_path, '100000_lines_symlink')
        symlink_digest = utils.digest(symlink_path)
        self.assertEqual(cache[symlink_digest][0], symlink_path)

        nested_file_path = os.path.join(self.resources_path, 'folder1/folder3/folder8/hello-2.10.tar.gz')
        nested_file_digest = utils.digest(nested_file_path)
        self.assertEqual(cache[nested_file_digest][0], nested_file_path)


    def test_cache_move(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            cache = Cache.build_cache(self.resources_path)

            file_path = os.path.join(self.resources_path, '100000_lines.md')
            file_digest = utils.digest(file_path)
            new_file_path = os.path.join(tmp_path, 'filename.md')
            cache.move_file(file_digest, new_file_path)
            self.assertEqual(cache[file_digest][0], new_file_path)
            self.assertEqual(cache.is_moved(file_digest), True)

            symlink_path = os.path.join(self.resources_path, '100000_lines_symlink')
            symlink_digest = utils.digest(symlink_path)
            new_symlink_path = os.path.join(tmp_path, 'symlink')
            cache.move_file(symlink_digest, new_symlink_path)
            self.assertEqual(cache[symlink_digest][0], new_symlink_path)
            self.assertEqual(cache.is_moved(symlink_digest), True)


