import os

class TreeNode:
    def __init__(self, name, children, is_file=False):
        self.name = name
        self.children = children
        self.is_file = is_file
    
    @staticmethod
    def build_tree_node(path, name):
        if os.path.isfile(path):
            return TreeNode(name, [], is_file=True)

        children = []

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            node = TreeNode.build_tree_node(item_path, item)
            children.append(node)
        
        return TreeNode(name, children) 

class Tree:
    
    def __init__(self, path, root): 
        self.path = path
        self.root = root

    @staticmethod
    def build_tree(path):
        root = TreeNode.build_tree_node(path, '')        
        return Tree(path, root)


