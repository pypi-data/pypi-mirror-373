
from base_test import BaseTest
from src.shadowshell.model.tree import Tree, TreeNode
from src.shadowshell.file.file_util import FileUtil

tree = Tree("/Users/shadowwalker/shadowshellxyz/ai-cloudkeeper-assets/kb/globalic/0000@留存线索录房示例")
tree.build(tree.get_root(), [])

def print_content(node):
    if node.leaf:
        print(FileUtil.get_all(node.code))

tree.bfs_traverse(tree.get_root(), [lambda node: print(node), lambda node : print_content(node)])

print("testTree")
