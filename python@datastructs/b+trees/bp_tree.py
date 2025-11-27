import bp_util as util
import random
import string
from graphviz import Digraph

class Node:
    def __init__(self, is_leaf):
        self.is_leaf = is_leaf

class INode(Node):
    def __init__(self, keys=None, children=None):
        super().__init__(is_leaf=False)
        self.keys = keys
        self.children = children

class LNode(Node):
    def __init__(self, keys=None, values=None, next=None):
        super().__init__(is_leaf=True)
        self.keys = keys
        self.values = values
        self.next = next

class Tree:
    '''
    B+ Constructor
        
    Parameters:
        node_capacity (int): the max amount of keys a node can hold
    '''
    def __init__(self, node_capacity):
        self.root: INode = None
        self.node_capacity = node_capacity
        
    def search(self, key) -> tuple:
        '''
        Search the B+ tree
        
        Parameters:
            key (int): key value to search for
            
        Returns:
            tuple (leaf, offset, path): 
                leaf (LNode): the leaf containing the key
                offset (int): offset to the key within the leaf
                path (list[Node]): a path representing the nodes traversed to the leaf
        '''
        
        # guard case
        if not self.root:
            return
        
        # traversal
        cur: Node = self.root
        path = [self.root]
        while not cur.is_leaf:
            keys = cur.keys

            # find first index where keys[i] >= key
            lb = util.bp_binary_search(keys, key)

            if lb >= len(keys):
                # key is greater than all separator keys -> go to rightmost child
                child_idx = len(cur.children) - 1
            else:
                if keys[lb] == key:
                    # key equals a separator: go to the child to the RIGHT
                    child_idx = lb + 1
                else:
                    # key lies between keys[lb-1] and keys[lb] -> go to child[lb]
                    child_idx = lb

            # traverse
            cur = cur.children[child_idx]
            path.append(cur)
        
        # at this point, cur is a leaf.
        key_idx = util.binary_search(cur.keys, key)
        if key_idx != -1:
            return (cur, key_idx, path)
        
        # not within leaf
        return (cur, None, path)
    
    # helper function for insert
    def split_up(self, path, p_idx, promote, new_child):
        # getting the child node
        child = path[p_idx + 1]

        # inserting the ascended key to the parent node
        parent: INode = path[p_idx]
                
        # index for splitting offset
        idx = parent.children.index(child)
        
        # adding the promoted key and child to the proper index
        parent.keys.insert(idx, promote)
        parent.children.insert(idx + 1, new_child)
        
        # handling overflows
        n = len(parent.keys)
        if n > self.node_capacity:
            # get the middle number for splitting
            mid = n // 2
            to_ascend = parent.keys[mid]
            
            # split, being careful
            right = INode(parent.keys[mid + 1:], parent.children[mid + 1:])
            
            # apply split
            parent.keys = parent.keys[:mid]
            parent.children = parent.children[:mid + 1]
            
            # special case with the root node. we've reached the top
            if self.root is parent:
                self.root = INode([to_ascend], [parent, right])
                return
            
            # else, we're a part of a non-root internal node -- recursive call
            self.split_up(path, p_idx - 1, to_ascend, right)
            
    def insert(self, key, value):
        # guard case
        if not self.root:
            self.root = LNode([key], [value], None)
            return
        
        # find the node with our key
        leaf, offset, path = self.search(key)
        
        # if this leaf happens to have our key, overwrite the value there with it
        if offset is not None:
            # leaf.keys[offset] = key
            leaf.values[offset] = value
            return
        
        # add our value to the existing leaf in order
        idx = util.insert_sorted(leaf.keys, key)
        leaf.values.insert(idx, value)
        
        # handle overflow
        n = len(leaf.keys)
        if n > self.node_capacity:
            # get the middle number for splitting
            mid = n // 2
            
            # split
            left = leaf
            
            # watch for python splitting weirdness
            right = LNode(leaf.keys[mid + 1:], leaf.values[mid + 1:], leaf.next)
            left.keys = left.keys[:mid + 1]
            left.values = left.values[:mid + 1]
            
            # plumbing
            left.next = right
            
            # promoting the first value of the right leaf
            promote = right.keys[0]
            
            # need to split upwards, handling root case
            if self.root is leaf:
                self.root = INode([promote], [left, right])
                return
            
            # leaf, but not the root. we need to tell the parent we've split. passing in the p_idx and the number to ascend
            self.split_up(path, -2, promote, right)

# -------------------
# TESTING FUNCTIONS
# -------------------
def to_graphviz(tree: Tree, filename="bptree", view=True):
    if tree.root is None:
        print("Empty tree")
        return
    
    # create directed graph
    dot = Digraph(comment="B+ Tree")
    dot.attr("node", shape="record", fontname="Courier")

    # track the leafs for making another pass
    leaf_ids = []

    def add_node(node: Node, node_id: int) -> int:
        """
        Recursively add nodes to the Digraph.
        node_id is a running counter so every node gets a unique name.
        Returns the next free node_id after using some.
        """
        this_id = f"n{node_id}"
        node_id += 1

        # make this node
        if node.is_leaf:
            # for leafs: label shows it's a leaf and its keys
            label = "{Leaf | " + " | ".join(str(k) for k in node.keys) + "}"
            dot.node(this_id, label=label, shape="box", color="blue")

            # add to leaf ids
            leaf_ids.append(this_id)
        else:
            # for internals: label shows it's an INode and its keys
            label = "{INode | " + " | ".join(str(k) for k in node.keys) + "}"
            dot.node(this_id, label=label, shape="record", color="black")

            # recurse on children
            for child in node.children:
                child_id = f"n{node_id}"
                node_id = add_node(child, node_id)
                dot.edge(this_id, child_id)

        return node_id

    # start recursion from the root with node_id = 0
    add_node(tree.root, 0)

    # once recursion ends, connect the leaves
    for i in range(len(leaf_ids) - 1):
            dot.edge(
                leaf_ids[i],
                leaf_ids[i + 1],
                style="dashed",
                color="gray",
                label="next",
                constraint="false",
            )

    # render to an svg
    dot.render(filename, format="svg", cleanup=True)
    if view:
        dot.view()

def random_value(length: int = 6) -> str:
    """Generate a random string value (so values aren't all the same)."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def stress_insert_random(tree: Tree, num_inserts: int = 1000, key_max: int = 10000):
    """
    Spam the B+ tree with a bunch of random inserts.

    Parameters:
        tree (Tree): your B+ tree instance
        num_inserts (int): how many inserts to perform
        key_max (int): keys will be in [0, key_max)
    """
    for i in range(num_inserts):
        k = random.randint(0, key_max - 1)
        v = f"val_{k}_{i}_{random_value(4)}"
        tree.insert(k, v)

    print(f"Done: inserted {num_inserts} random keys (0..{key_max - 1}).")

if __name__ == "__main__":
    # test cases
    tree = Tree(10)
    stress_insert_random(tree, num_inserts=2000, key_max=2000)

    to_graphviz(tree, "bp_tree_example")
