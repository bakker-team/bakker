import json
import os

class TreeNode:
    def __init__(self, name, children, is_file=False):
        self.name = name
        self.children = children
        self.is_file = is_file

    def to_dict(self):
        return {
                'name': self.name,
                'children': [child.to_dict() for child in self.children],
                'is_file': self.is_file
               }

    @staticmethod
    def build_tree_node(path, name):
        if os.path.isfile(path) or os.path.islink(path):
            return TreeNode(name, [], is_file=True)

        children = []

        for item in os.listdir(path):
            item_path = os.path.join(path, item)

            node = TreeNode.build_tree_node(item_path, item)
            children.append(node)

        return TreeNode(name, children)

    @staticmethod
    def from_dict(d):
        return TreeNode(d['name'], [TreeNode.from_dict(child) for child in d['children']], is_file=d['is_file'])

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

