#!/usr/bin/env python3


class BinarySearchTree:
    """A simple, recursive binary tree implementation. Each tree holds pointers to subtrees."""

    def __init__(self):
        """Initializes an empty tree."""
        self.root = None

    def insert(self, key):
        """Adds key to the tree. No return."""

        if self.root is None:
            # Base case: no tree. Insert at root.
            self.root = BinarySearchTree.Node(key)
        else:
            self.root.insert(key)

    def search(self, key):
        """Retrieves the key from the tree, or None if not present."""
        if self.root is None:
            return None
        return self.root.search(key)

    def delete(self, key):
        """Deletes the first-found occurrence of Key from the tree, as determined by equality (==).

        Returns True if key was found and deleted and False if key was not found."""

        if self.root is None:
            # Base case: no tree here.
            return False

        if self.root.key == key:
            # Base case: delete root.
            self.root = self.root.replace()
            return True

        # Otherwise, search the tree.
        return self.root.delete(key)

    class Node:
        def __init__(self, key):
            self.left = None
            self.right = None
            self.key = key

        def insert(self, key):
            """Recursive insertion function to add key to tree. Caller must handle the base case of an empty tree."""

            # Traverse to a leaf.
            if key < self.key:
                # Go left.
                if self.left is None:
                    # Left is free.
                    self.left = BinarySearchTree.Node(key)
                else:
                    # Left is occupied. Recurse.
                    self.left.insert(key)
            else:
                # Go right.
                if self.right is None:
                    # Right is free.
                    self.right = BinarySearchTree.Node(key)
                else:
                    # Right is occupied. Recurse.
                    self.right.insert(key)

        def search(self, key):
            """Retrieves the key from the tree, or None if not present."""

            if self.key == key:
                # Base case: key found.
                return self.key

            if key < self.key and type(self.left) is BinarySearchTree.Node:
                # Go left.
                return self.left.search(key)
            elif type(self.right) is BinarySearchTree.Node:
                # Go right.
                return self.right.search(key)
            else:
                # We've fallen out of the tree.
                return None

        def delete(self, key):
            """Recursive helper. Caller must ensure that this Node is NOT the Node to remove!"""

            if key < self.key:
                if self.left is None:
                    return False
                if self.left.key == key:
                    # Delete left.
                    self.left = self.left.replace()
                    return True
                # Else, keep searching.
                return self.left.delete(key)
            else:
                # Search right subtree.
                if self.right is None:
                    return False
                if self.right.key == key:
                    # Delete right.
                    self.right = self.right.replace()
                    return True
                # Else, keep searching.
                return self.right.delete(key)

        def replace(self):
            """Helper function for deleting Nodes. Prepares this Node's successor and returns it.

            First, finds the inorder successor of this Node.
            Then, replaces this Node with its inorder successor in the tree (unless this Node is a leaf).
            Finally, returns the new root Node of the subtree formerly rooted at this Node, or None if this was a leaf.

            The caller should assign this returned value to the appropriate place in the larger tree (or as root)."""

            if self.left is None and self.right is None:
                # Leaf.
                return None

            if self.left is None:
                # No left tree, but there's a right tree. No further work necessary.
                return self.right

            if self.right is None:
                # No right tree, but there's a left tree. No further work necessary.
                return self.left

            if self.right.left is None:
                # Left and right trees, but right child has no left child.
                # Link right child to replace self.
                self.right.left = self.left
                return self.right

            # We have left and right subtrees. Find the inorder successor and attach it.
            ios = self.fetchIOS()
            ios.left = self.left
            ios.right = self.right
            return ios

        def fetchIOS(self):
            """Helper function to fetch and prepare the inorder successor of a Node that's being deleted.

            This method assumes that the caller has checked all simpler cases and that the replacement Node really is
            the leftmost descendant of the Node's right child.

            First, it finds the correct inorder successor by checking the right child, and then traversing left
            as far as possible. It then detaches the successor from the tree

            Finally, it returns the freed Node, which is ready to be attached where it is needed."""

            # We'll loop with a previous pointer for efficiency and ease of access. The alternative is to recurse with a
            # lookahead, i.e. recurse until self.left.left is None. And that's no good.

            # Initialize with curr as the right child, then traverse left as needed.
            prev = self
            curr = self.right
            while type(curr.left) is BinarySearchTree.Node:
                prev = curr
                curr = curr.left

            # Now, prev is the parent of the IOS and curr is the IOS!

            # Reattach the right subtree of the IOS, if any; if None, this will zero prev.left automatically.
            prev.left = curr.right

            # Now detach the IOS.
            curr.right = None

            # Finally, return it so it can be reattached.
            return curr