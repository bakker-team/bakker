import os
import tempfile
import unittest

from bakker.checkpoint import Checkpoint
from bakker.storage import FileSystemStorage


class TestCheckpointNames(unittest.TestCase):
    def setUp(self):
        self.resources_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../resources/tests/backup_indexing_test_folder')

    def test_checkpoint_file_without_name(self):
        checkpoint = Checkpoint.build_checkpoint(self.resources_path)
        with tempfile.TemporaryDirectory() as tmp_path:
            storage = FileSystemStorage(tmp_path)
            storage.store(self.resources_path, checkpoint)

            meta = storage.retrieve_checkpoint_metas()[0]
        
        self.assertEqual(meta.checksum, checkpoint.root.checksum)
        self.assertEqual(meta.time, checkpoint.time)
        self.assertIs(meta.name, None)

    def test_checkpoint_file_with_name(self):
        checkpoint = Checkpoint.build_checkpoint(self.resources_path, 'my_test_name')
        with tempfile.TemporaryDirectory() as tmp_path:
            storage = FileSystemStorage(tmp_path)
            storage.store(self.resources_path, checkpoint)

            meta = storage.retrieve_checkpoint_metas()[0]

        self.assertEqual(meta.checksum, checkpoint.root.checksum)
        self.assertEqual(meta.time, checkpoint.time)
        self.assertEqual(meta.name, checkpoint.name)

    def test_checkpoint_retrieval(self):
        checkpoint = Checkpoint.build_checkpoint(self.resources_path, 'my_test_name')
        with tempfile.TemporaryDirectory() as tmp_path:
            storage = FileSystemStorage(tmp_path)
            storage.store(self.resources_path, checkpoint)

            meta = storage.retrieve_checkpoint_metas()[0]
            checkpoint_2 = storage.retrieve_checkpoint(meta)

        self.assertEqual(checkpoint.time, checkpoint_2.time)
        self.assertEqual(checkpoint.name, checkpoint_2.name)
        self.assertEqual(checkpoint.meta.checksum, checkpoint_2.meta.checksum)

        self.assertEqual(checkpoint.root.checksum, checkpoint_2.root.checksum)
