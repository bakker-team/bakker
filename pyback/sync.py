from abc import ABC, abstractmethod
import os
import shutil

import xxhash

from pyback.tree import Tree, FileNode, SymlinkNode


class Storage(ABC):
    @abstractmethod
    def has_file(self, file_hash):
        pass

    @abstractmethod
    def send_file(self, file_path, file_hash):
        pass

    @abstractmethod
    def receive_file(self, file_path, file_hash):
        pass

    @abstractmethod
    def send_tree(self, tree, key):
        pass

    @abstractmethod
    def receive_tree_keys(self):
        pass

    @abstractmethod
    def receive_tree(self, key):
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

    def has_file(self, file_hash):
        return os.path.isfile(os.path.join(self.file_path, file_hash + self.FILE_EXT))

    def send_file(self, file_path, file_hash):
        dst_file_path = os.path.join(self.file_path, file_hash + self.FILE_EXT)
        if os.path.isfile(dst_file_path):
            raise FileExistsError(file_hash)
        if not os.path.exists(os.path.dirname(dst_file_path)):
            os.makedirs(os.path.dirname(dst_file_path))
        shutil.copyfile(file_path, dst_file_path, follow_symlinks=False)

    def receive_file(self, file_path, file_hash):
        src_file_path = os.path.join(self.file_path, file_hash + self.FILE_EXT)
        if not os.path.isfile(src_file_path):
            raise FileNotFoundError(file_hash)
        shutil.copyfile(src_file_path, file_path)

    def send_tree(self, tree, key):
        tree_file_path = os.path.join(self.tree_path, key + self.TREE_FILE_EXT)
        if os.path.isfile(tree_file_path):
            raise FileExistsError(key)
        if not os.path.exists(os.path.dirname(tree_file_path)):
            os.makedirs(os.path.dirname(tree_file_path))
        with open(tree_file_path, 'w') as f:
            f.write(tree.to_json())

    def receive_tree_keys(self):
        return [key[:-len(self.TREE_FILE_EXT)] for key in os.listdir(self.tree_path) if key[-len(self.TREE_FILE_EXT):] == self.TREE_FILE_EXT]

    def receive_tree(self, key):
        tree_file_path = os.path.join(self.tree_path, key + self.TREE_FILE_EXT)
        if not os.path.is_file(tree_file_path):
            raise FileNotFoundError(key)
        with open(tree_file_path, 'r') as f:
            return Tree.from_json(f.read(), '')


def send(connector, tree):
    for node, node_path in tree.dfs_iter():
        if isinstance(node, FileNode) and not connector.has_file(node.checksum):
            connector.send_file(node_path, node.checksum)
        elif isinstance(node, SymlinkNode) and not connector.has_file(node.checksum):
            connector.send_file(node_path, node.checksum)

    message = xxhash.xxh64()
    message.update(tree.time.isoformat())
    key = message.hexdigest()

    connector.send_tree(tree, key)
