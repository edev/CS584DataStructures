import unittest
from binarysearchtree import BinarySearchTree
import random


class MyTestCase(unittest.TestCase):
    def test_basic_checks(self):
        bst = BinarySearchTree()

        # Root node: 7
        bst.insert(7)
        self.assertEqual(7, bst.root.key, "Insert key as root")

        #   7
        #  /
        # 3
        bst.insert(3)
        self.assertEqual(3, bst.root.left.key, "Insert key as root's left child")

        #   7
        #  / \
        # 3   11
        bst.insert(11)
        self.assertEqual(11, bst.root.right.key, "Insert key as root's right child")

        #     7
        #    / \
        #   3   11
        #  /
        # 1
        bst.insert(1)
        self.assertEqual(1, bst.root.left.left.key, "Insert key as left child of non-root node")

        #     7
        #    / \
        #   3   11
        #  /     \
        # 1       13
        bst.insert(13)
        self.assertEqual(13, bst.root.right.right.key, "Insert key as right child of non-root node")

        #     7
        #    / \
        #   3   11
        #  /   / \
        # 1   9   13
        bst.insert(9)
        self.assertEqual(9, bst.root.right.left.key, "Insert key as left child of right child")

        #      7
        #    /   \
        #   3     11
        #  / \    / \
        # 1   5  9   13
        bst.insert(5)
        self.assertEqual(5, bst.root.left.right.key, "Insert key as right child of left child")

        for i in range(1, 14, 2):
            self.assertEqual(i, bst.search(i), "Search full tree for {}.".format(i))

        for i in range(0, 15, 2):
            self.assertIsNone(bst.search(i), "Search full tree for nonexistent items.")

        # By adding a few more elements, we can test all basic deletion cases with a bit of planning.
        # (Some corner cases may not be covered, e.g. testing whether a replacement works with both None and Node)
        #      7
        #    /   \
        #   3     11
        #  / \    / \
        # 1   5  9   13
        #       /   /
        #      8  12
        bst.insert(8)
        bst.insert(12)

        # Possible deletion cases:
        # A - delete root with successor as leftmost child of right subtree (IOS)
        # B - delete root with left and right children, right has no left subtree
        # C - delete root with only right child
        # D - delete root with only left child
        # E - delete root with no children, leaving an empty tree
        # F - delete non-root node with successor as leftmost child of right subtree (IOS)
        # G - delete non-root node with only right child
        # H - delete non-root node with only left child
        # I - delete non-root node with left and right children, right child is a leaf
        # J - delete non-root leaf

        # Deletions, in order, matched with cases above:
        # 7  - A
        # 3  - I
        # 11 - F
        # 9  - J
        # 5  - H
        # 12 - G
        # 8  - B
        # 13 - D
        # This leaves a tree with one node, 1.

        # Then we'll insert 2 to form the tree
        #    1
        #     \
        #      2
        # And we'll delete:
        # 1 - C
        # 2 - E

        for i in [7, 3, 11, 9, 5, 12, 8, 13]:
            self.assertTrue(bst.delete(i), "Test deletion cases")
            self.assertIsNone(bst.search(i), "Search for deleted item")

        bst.insert(2)
        for i in [1, 2]:
            self.assertTrue(bst.delete(i), "Test deletion cases")
            self.assertIsNone(bst.search(i), "Search for deleted item")

        self.assertFalse(bst.delete(6), "Delete item that's not in the tree")
        self.assertFalse(bst.delete(7), "Delete item previously removed from tree")
        self.assertIsNone(bst.search(1), "Search empty tree")

    def test_fuzz(self):
        """Perform some basic randomized input testing."""
        repeat_times = 5
        sample_set = range(-1000, 1001)

        bst = BinarySearchTree()
        for i in range(repeat_times):
            # Insert elements
            for j in random.sample(sample_set, len(sample_set)):
                bst.insert(j)

            # Search for elements
            for j in random.sample(sample_set, len(sample_set)):
                self.assertEqual(j, bst.search(j))

            # Delete elements
            for j in random.sample(sample_set, len(sample_set)):
                self.assertTrue(bst.delete(j))
                self.assertIsNone(bst.search(j))

if __name__ == '__main__':
    unittest.main()
