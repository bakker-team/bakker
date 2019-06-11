from os import path

from bakker.checkpoint import Checkpoint, SymlinkNode, FileNode


class Cache:
    def __init__(self, index):
        # Mapping from file hashes to a tuple (file_path, is_moved).
        # The flag is_moved is used to determine whether we have to copy the cached file instead
        # of just moving it to a new location. This is relevant for duplicate files.
        self.index = index

    @staticmethod
    def build_cache(dir_path):
        checkpoint = Checkpoint.build_checkpoint(dir_path)
        index = {}
        for node, rel_path in checkpoint.iter():
            if isinstance(node, FileNode) or isinstance(node, SymlinkNode):
                index[node.checksum] = (path.join(dir_path, rel_path), False)

        return Cache(index)

    def __getitem__(self, item):
        return self.index[item]

    def move_file(self, file_digest, new_path):
        self.index[file_digest] = (new_path, True)

    def is_moved(self, file_digest):
        return self.index[file_digest][1]
