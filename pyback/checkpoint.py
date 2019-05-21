from datetime import datetime
import json
import os
import re
import stat

from .utils import get_file_digest, get_symlink_digest, get_directory_digest, datetime_from_iso_format


class TreeNode:
    def __init__(self, name, checksum, permissions):
        self.name = name
        self.checksum = checksum
        self.permissions = permissions

    def to_dict(self):
        raise NotImplementedError()

    @staticmethod
    def build_tree_node(path, name):
        file_permissions = stat.S_IMODE(os.lstat(path).st_mode)

        if os.path.islink(path):
            return SymlinkNode(name, get_symlink_digest(path), file_permissions)
        elif os.path.isfile(path):
            return FileNode(name, get_file_digest(path), file_permissions)
        elif os.path.isdir(path):
            children = dict()

            for child_name in os.listdir(path):
                child_path = os.path.join(path, child_name)
                if not os.path.isfile(child_path) and not os.path.isdir(child_path):
                    print("Ignored: " + child_path)
                    continue
                children[child_name] = TreeNode.build_tree_node(child_path, child_name)

            child_checksums = [children[child_name].checksum for child_name in sorted(children.keys())]
            directory_digest = get_directory_digest(*child_checksums)
            return DirectoryNode(name, directory_digest, file_permissions, children)
        
        print('Could not backup: ' + path)

    @staticmethod
    def from_dict(d):
        if d['type'] == 'directory':
            return DirectoryNode.from_dict(d)
        elif d['type'] == 'file':
            return FileNode.from_dict(d)
        elif d['type'] == 'symlink':
            return SymlinkNode.from_dict(d)

        raise TypeError('Type ' + d['name'] + ' does not exist.')


class DirectoryNode(TreeNode):
    def __init__(self, name, checksum, permissions, children):
        super().__init__(name, checksum, permissions)
        self.children = children

    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'permissions': self.permissions,
                'children': [child.to_dict() for child in self.children.values()],
                'type': 'directory',
               }

    @staticmethod
    def from_dict(d):
        return DirectoryNode(d['name'], d['checksum'], d['permissions'], {child['name']: TreeNode.from_dict(child) for child in d['children']})


class FileNode(TreeNode):
    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'permissions': self.permissions,
                'type': 'file',
               }

    @staticmethod
    def from_dict(d):
        return FileNode(d['name'], d['checksum'], d['permissions'])


class SymlinkNode(TreeNode):
    def to_dict(self):
        return {
                'name': self.name,
                'checksum': self.checksum,
                'permissions': self.permissions,
                'type': 'symlink',
               }

    @staticmethod
    def from_dict(d):
        return SymlinkNode(d['name'], d['checksum'], d['permissions'])


class Checkpoint:
    def __init__(self, root, time=None, name=None):
        assert name is None or re.match('^[a-zA-Z0-9_\-.]+$', name)

        self.root = root
        self.time = datetime.now() if time is None else time
        self.name = name

    @property
    def meta(self):
        return CheckpointMeta(self.root.checksum, self.time, self.name)

    def to_json(self):
        return json.dumps(dict(root=self.root.to_dict(), time=self.time.isoformat(), name=self.name), indent=2)

    def iter(self):
        stack = [(self.root, '')]
        while len(stack):
            current_node, current_path = stack.pop()
            yield current_node, current_path

            if isinstance(current_node, DirectoryNode):
                for child_name, child_node in current_node.children.items():
                    stack.append((child_node, os.path.join(current_path, child_name)))

    @staticmethod
    def build_checkpoint(path, name=None):
        root = TreeNode.build_tree_node(path, '')
        return Checkpoint(root, name=name)

    @staticmethod
    def from_json(json_str):
        tree_dict = json.loads(json_str)

        return Checkpoint(TreeNode.from_dict(tree_dict['root']), time=datetime_from_iso_format(tree_dict['time']), name=tree_dict['name'])


class CheckpointMeta:
    def __init__(self, checksum, time, name):
        self.checksum = checksum
        self.time = time
        self.name = name

    def to_string(self):
        timestring = self.time.isoformat()
        timestring += '.000000' if len(timestring) == 19 else ''

        return self.checksum + '_' + timestring  + ('_' + self.name if self.name else '')

    @staticmethod
    def from_string(string):
        boom = string.split('_', 2)
        checksum = boom[0]
        time = datetime_from_iso_format(boom[1])
        name = None if len(boom) == 2 else boom[2]
        return CheckpointMeta(checksum, time, name)
