import json
import os

from .utils import get_file_digest, get_symlink_digest, get_directory_digest


class TreeNode:
    def __init__(self, name, checksum):
        self.name = name
        self.checksum = checksum

    def to_dict(self):
        raise NotImplementedError()

    @staticmethod
    def build_tree_node(path, name):
        if os.path.isfile(path) and not os.path.islink(path):
            return FileNode(name, get_file_digest(path))
        elif os.path.islink(path):
            return SymlinkNode(name, get_symlink_digest(path))
        elif os.path.isdir(path):
            children = dict()

            for child_name in os.listdir(path):
                child_path = os.path.join(path, child_name)
                children[child_name] = TreeNode.build_tree_node(child_path, child_name)

            child_checksums = [children[child_name].checksum for child_name in sorted(children.keys())]
            directory_digest = get_directory_digest(*child_checksums)
            return DirectoryNode(name, directory_digest, children)
        
        raise Error('Unknown content.')

    @staticmethod
    def from_dict(d):
        if d['type'] == 'directory':
            return DirectoryNode.from_dict(d)
        elif d['type'] == 'file':
            return FileNode.from_dict(d)
        elif d['type'] == 'symlink':
            return SymlinkNode.from_dict(d)

        raise Error('Type ' + d['name'] + ' does not exist.')


class DirectoryNode(TreeNode):
    def __init__(self, name, checksum, children):
        super().__init__(name, checksum)
        self.children = children

    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'children': [child.to_dict() for child in self.children.values()],
                'type': 'directory',
               }

    @staticmethod
    def from_dict(d):
        return DirectoryNode(d['name'], d['checksum'], {child['name']: TreeNode.from_dict(child) for child in d['children']})


class FileNode(TreeNode):
    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'type': 'file',
               }

    @staticmethod
    def from_dict(d):
        return FileNode(d['name'], d['checksum'])


class SymlinkNode(TreeNode):
    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'type': 'symlink',
               }

    def from_dict(d):
        return SymlinkNode(d['name'], d['checksum'])


class Tree:
    def __init__(self, path, root):
        self.path = path
        self.root = root

    def to_json(self):
        return json.dumps(self.root.to_dict(), indent=2)

    @staticmethod
    def build_tree(path):
        root = TreeNode.build_tree_node(path, '')
        return Tree(path, root)

    @staticmethod
    def from_json(json_str, path):
        root = TreeNode.from_dict(json.loads(json_str))
        return Tree(path, root)

