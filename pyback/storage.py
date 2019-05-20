from abc import ABC, abstractmethod
import os
import shutil

import xxhash

from pyback.checkpoint import Checkpoint, FileNode, SymlinkNode, DirectoryNode


class Storage(ABC):
    @abstractmethod
    def has_file(self, checksum):
        pass

    # remove file path -> the storage should decide where and how to store the file
    @abstractmethod
    def store_file(self, file_path, checksum):
        pass

    @abstractmethod
    def retrieve_file(self, checksum, dst_file_path):
        pass

    @abstractmethod
    def store_checkpoint(self, checkpoint, checkpoint_id):
        pass

    @abstractmethod
    def retrieve_checkpoint_ids(self):
        pass

    @abstractmethod
    def retrieve_checkpoint(self, checkpoint_id):
        pass


class FileSystemStorage(Storage):
    TREE_DIR = 'checkpoints'
    FILE_DIR = 'files'
    TREE_FILE_EXT = '.json'
    FILE_EXT = ''
    
    def __init__(self, path):
        self.path = path
        self.tree_path = os.path.join(path, self.TREE_DIR)
        self.file_path = os.path.join(path, self.FILE_DIR)

    def has_file(self, checksum):
        return os.path.isfile(os.path.join(self.file_path, checksum + self.FILE_EXT))

    def store_file(self, src_file_path, checksum):
        dst_file_path = os.path.join(self.file_path, checksum + self.FILE_EXT)
        if os.path.isfile(dst_file_path):
            raise FileExistsError(checksum)
        if not os.path.exists(os.path.dirname(dst_file_path)):
            os.makedirs(os.path.dirname(dst_file_path))
        shutil.copyfile(src_file_path, dst_file_path, follow_symlinks=False)

    def retrieve_file(self, checksum, dst_file_path):
        src_file_path = os.path.join(self.file_path, checksum + self.FILE_EXT)
        # checks existence and returns true for broken symlinks
        if not os.path.lexists(src_file_path):
            raise FileNotFoundError(checksum)
        shutil.copyfile(src_file_path, dst_file_path, follow_symlinks=False)

    def store_checkpoint(self, checkpoint, checkpoint_id):
        tree_file_path = os.path.join(self.tree_path, checkpoint_id + self.TREE_FILE_EXT)
        if os.path.isfile(tree_file_path):
            raise FileExistsError(checkpoint_id)
        if not os.path.exists(os.path.dirname(tree_file_path)):
            os.makedirs(os.path.dirname(tree_file_path))
        with open(tree_file_path, 'w') as f:
            f.write(checkpoint.to_json())

    # TODO We should probably also retrieve some metadata about the checkpoint
    #  except from the name to allow the user to chose between checkpoints depending on a timestamp, name etc.
    def retrieve_checkpoint_ids(self):
        return [checkpoint[:-len(self.TREE_FILE_EXT)] for checkpoint in os.listdir(self.tree_path) if checkpoint[-len(self.TREE_FILE_EXT):] == self.TREE_FILE_EXT]

    def retrieve_checkpoint(self, checkpoint_id):
        checkpoint_file_path = os.path.join(self.tree_path, checkpoint_id + self.TREE_FILE_EXT)
        if not os.path.isfile(checkpoint_file_path):
            raise FileNotFoundError(checkpoint_id)
        with open(checkpoint_file_path, 'r') as f:
            return Checkpoint.from_json(f.read())


def store(src_dir_path, storage, checkpoint):
    for node, relative_node_path in checkpoint.iter():
        absolute_node_path = os.path.join(src_dir_path, relative_node_path)
        if isinstance(node, FileNode) and not storage.has_file(node.checksum):
            storage.store_file(absolute_node_path, node.checksum)
        elif isinstance(node, SymlinkNode) and not storage.has_file(node.checksum):
            storage.store_file(absolute_node_path, node.checksum)

    message = xxhash.xxh64()
    message.update(checkpoint.time.isoformat())
    checkpoint_id = message.hexdigest()

    storage.store_checkpoint(checkpoint, checkpoint_id)

def retrieve(storage, checkpoint_id, dst_dir_path):
    checkpoint = storage.retrieve_checkpoint(checkpoint_id)
    for item, relative_item_path in checkpoint.iter():
        item_path = os.path.join(dst_dir_path, relative_item_path)
        if isinstance(item, DirectoryNode) and not os.path.exists(item_path):
            os.mkdir(item_path, item.permissions)
        if isinstance(item, SymlinkNode) or isinstance(item, FileNode):
            item_path = os.path.join(dst_dir_path, relative_item_path)
            storage.retrieve_file(item.checksum, item_path)





