#!/usr/bin/env python3


class BinarySearchTree:
    """A simple, iterative binary tree implementation. Each tree holds pointers to subtrees."""

    legend_text = "Binary Search Tree"

    def __init__(self):
        """Initializes an empty tree."""
        self.root = None

    def insert(self, key):
        """Adds key to the tree. No return."""

        if self.root is None:
            # Base case: no tree. Insert at root.
            self.root = BinarySearchTree.Node(key)
            return

        # Iterative version of recursive insertion method.
        current = self.root
        while True:
            # Traverse to a leaf.
            if key < current.key:
                # Go left.
                if current.left is None:
                    # Leaf. Insert here. Base case.
                    current.left = BinarySearchTree.Node(key)
                    break
                else:
                    # Keep traversing.
                    current = current.left
            else:
                # Go right.
                if current.right is None:
                    # Leaf. Insert here. Base case.
                    current.right = BinarySearchTree.Node(key)
                    break
                else:
                    # Keep traversing.
                    current = current.right


    def search(self, key):
        """Retrieves the key from the tree, or None if not present."""
        if self.root is None:
            return None

        current = self.root
        while current is not None and current.key != key:
            if key < current.key:
                current = current.left
            else:
                current = current.right
        if current is None:
            return None
        return current.key

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
        current = self.root
        while True:
            if key < current.key:
                if current.left is None:
                    return False
                elif key == current.left.key:
                    current.left = current.left.replace()
                    return True
                else:
                    current = current.left
            else:
                if current.right is None:
                    return False
                elif key == current.right.key:
                    current.right = current.right.replace()
                    return True
                else:
                    current = current.right


    class Node:
        def __init__(self, key):
            self.left = None
            self.right = None
            self.key = key

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