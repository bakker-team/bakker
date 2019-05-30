from abc import ABC, abstractmethod
import os
import shutil

from bakker.checkpoint import Checkpoint, FileNode, SymlinkNode, DirectoryNode, CheckpointMeta


class Storage(ABC):
    @abstractmethod
    def has_file(self, checksum):
        pass

    @abstractmethod
    def store_file(self, file_path, checksum):
        pass

    @abstractmethod
    def retrieve_file(self, checksum, dst_file_path, file_permissions):
        pass

    @abstractmethod
    def store_checkpoint(self, checkpoint):
        pass

    @abstractmethod
    def retrieve_checkpoint_metas(self):
        pass

    @abstractmethod
    def retrieve_checkpoint(self, checkpoint_meta):
        pass

    @abstractmethod
    def store(self, src_dir_path, checkpoint):
        pass

    @abstractmethod
    def retrieve(self, dst_dir_path, checkpoint_meta):
        pass

    @abstractmethod
    def retrieve_by_checksum(self, dst_dir_path, checksum):
        pass

    @abstractmethod
    def retrieve_by_name(self, dst_dir_path, checksum):
        pass


class FileSystemStorage(Storage):
    TREE_DIR = 'checkpoints'
    FILE_DIR = 'files'
    TREE_FILE_EXT = '.json'
    FILE_EXT = ''
    REMOTE_PERMISSIONS = 0o440

    def __init__(self, path):
        self.path = path
        self.tree_path = os.path.join(path, self.TREE_DIR)
        self.file_path = os.path.join(path, self.FILE_DIR)

    def has_file(self, checksum):
        return os.path.lexists(os.path.join(self.file_path, checksum + self.FILE_EXT))

    def store_file(self, src_file_path, checksum):
        """ Stores a single file at the backup location

        :param src_file_path: the file at the src_file_path is backed up to the storage location
        :param checksum: identifies the file in the backup location

        :raises IOError: If the source is not readable or the destination is not writable.
        """
        dst_file_path = os.path.join(self.file_path, checksum + self.FILE_EXT)

        if os.path.isfile(dst_file_path):
            raise FileExistsError(checksum)
        if not os.path.exists(os.path.dirname(dst_file_path)):
            os.makedirs(os.path.dirname(dst_file_path))

        shutil.copy2(src_file_path, dst_file_path, follow_symlinks=False)
        if not os.path.islink(dst_file_path):
            os.chmod(dst_file_path, self.REMOTE_PERMISSIONS)

    def retrieve_file(self, checksum, dst_file_path, file_permissions):
        """ Retrieves a single file from the backup location

        :param checksum: identifies the file in the backup location
        :param dst_file_path: the file is copied to this destination
        :param file_permissions: int that represents the file permissions (e.g. 0o644)

        :raises IOError: If the source is not readable or the destination is not writable.
        """
        src_file_path = os.path.join(self.file_path, checksum + self.FILE_EXT)
        # checks existence and returns true for broken symlinks
        if not os.path.lexists(src_file_path):
            raise FileNotFoundError(checksum)

        shutil.copy2(src_file_path, dst_file_path, follow_symlinks=False)
        if not os.path.islink(dst_file_path):
            os.chmod(dst_file_path, file_permissions)

    def store_checkpoint(self, checkpoint):
        tree_file_path = os.path.join(self.tree_path, checkpoint.meta.to_string() + self.TREE_FILE_EXT)
        if os.path.isfile(tree_file_path):
            raise FileExistsError(checkpoint)
        if not os.path.exists(os.path.dirname(tree_file_path)):
            os.makedirs(os.path.dirname(tree_file_path))
        with open(tree_file_path, 'w') as f:
            f.write(checkpoint.to_json())

    def retrieve_checkpoint_metas(self):
        if not os.path.isdir(self.tree_path):
            return []
        return [CheckpointMeta.from_string(checkpoint_file[:-len(self.TREE_FILE_EXT)])
                for checkpoint_file in os.listdir(self.tree_path)
                if checkpoint_file[-len(self.TREE_FILE_EXT):] == self.TREE_FILE_EXT]

    def retrieve_checkpoint(self, checkpoint_meta):
        if not os.path.isdir(self.tree_path):
            return
        checkpoint_files = [c for c in os.listdir(self.tree_path)
                            if c[-len(self.TREE_FILE_EXT):] == self.TREE_FILE_EXT]

        checkpoint_file = checkpoint_meta.to_string() + self.TREE_FILE_EXT
        if checkpoint_file in checkpoint_files:
            with open(os.path.join(self.tree_path, checkpoint_file), 'r') as f:
                return Checkpoint.from_json(f.read())

    def store(self, src_dir_path, checkpoint):
        for node, relative_node_path in checkpoint.iter():
            absolute_node_path = os.path.join(src_dir_path, relative_node_path)
            if isinstance(node, FileNode) and not self.has_file(node.checksum):
                self.store_file(absolute_node_path, node.checksum)
            elif isinstance(node, SymlinkNode) and not self.has_file(node.checksum):
                self.store_file(absolute_node_path, node.checksum)

        self.store_checkpoint(checkpoint)

    def retrieve(self, dst_dir_path, checkpoint_meta):
        checkpoint = self.retrieve_checkpoint(checkpoint_meta)
        for item, relative_item_path in checkpoint.iter():
            item_path = os.path.join(dst_dir_path, relative_item_path)
            if isinstance(item, DirectoryNode) and not os.path.exists(item_path):
                os.mkdir(item_path, item.permissions)
            if isinstance(item, SymlinkNode) or isinstance(item, FileNode):
                item_path = os.path.join(dst_dir_path, relative_item_path)
                self.retrieve_file(item.checksum, item_path, item.permissions)

    def retrieve_by_checksum(self, dst_dir_path, checksum):
        checkpoint_metas = self.retrieve_checkpoint_metas()

        checkpoint_meta_candidates = []
        for checkpoint_meta in checkpoint_metas:
            if checkpoint_meta.checksum[:len(checksum)] == checksum:
                checkpoint_meta_candidates.append(checkpoint_meta)

        if len(checkpoint_meta_candidates) == 0:
            raise FileNotFoundError(checksum)
        elif len(checkpoint_meta_candidates) == 1:
            self.retrieve(dst_dir_path, checkpoint_meta_candidates[0])
        else:
            raise NoUniqueMatchError(checksum)

    def retrieve_by_name(self, dst_dir_path, name):
        checkpoint_metas = self.retrieve_checkpoint_metas()

        checkpoint_meta_candidates = []
        for checkpoint_meta in checkpoint_metas:
            if checkpoint_meta.name == name:
                checkpoint_meta_candidates.append(checkpoint_meta)

        if len(checkpoint_meta_candidates) == 0:
            raise FileNotFoundError(name)
        elif len(checkpoint_meta_candidates) == 1:
            self.retrieve(dst_dir_path, checkpoint_meta_candidates[0])
        else:
            raise NoUniqueMatchError(name)


class NoUniqueMatchError(LookupError):
    pass
