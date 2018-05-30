import random
import sys
import statistics
from datastructures.binarysearchtree import BinarySearchTree
from datastructures.toastdriven_pyskip import Skiplist as PySkip
from datastructures.stromberg_treap import treap as StrombergTreap
from datastructures.jenks_treap import Treap as JenksTreap
from datastructures.pyskiplist.skiplist import SkipList as PySkipList
# from datastructures.redblacktree import RedBlackTree
from datastructures.avltree import BinaryTree as AVLTree
from datastructures.enether_rbtree import RedBlackTree
from pgfplot import PgfPlot
from sidgraphset import SIDGraphSet, SIDBenchmark
from mixedsidbenchmarkplot import MixedSIDBenchmarkPlot


# TABLE OF CONTENTS:
# This file is divided into the following sections, denoted by prominent SECTION comments.
#
#   - Graph default configuration
#   - Input set generators
#   - Graph generation functions
#   - Graph definitions
#   - Graph invocations


# =====================================
# SECTION: Global default configuration
# =====================================


# Constants defining benchmark behavior. See BenchmarkPlot in plot.py for details.
START = 0
BENCHMARK_START = 100000
BENCHMARK_LENGTH = 1000
BENCHMARK_INTERVAL = 20000
STOP = BENCHMARK_START * 10 + BENCHMARK_LENGTH
REPEAT = 1
COMBINE_METHOD = statistics.median

# Produce this many graph .tex files for each graph - so you can choose the best data set later in LaTeX.
DATA_SETS_TO_PRODUCE = 3

# Convenience constant for generating samples of the same size as the benchmark
SAMPLE_SIZE = STOP - START

# Constants determining default graph labels. Override in the call to graph() if desired.
XLABEL = "Number of items in data structure"
YLABEL = "Running time (seconds)"


# =============================
# SECTION: Input set generators
# =============================


def generateRandomSamples(n=SAMPLE_SIZE):
    """Returns an n-sized array populated with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
    return random.sample(list(range(n)), n)


def generateRandomSIDSampleSet(
        stop=STOP,
        bm_start=BENCHMARK_START,
        bm_length=BENCHMARK_LENGTH,
        bm_interval=BENCHMARK_INTERVAL
):
    """Generates 3 random sample sets suitable for passing into an SIDBenchmark.

    Returns a triple of (search_samples, insert_samples, delete_samples).

    search_samples: contains random samples from the elements that have been inserted in each benchmark section.
    insert_samples: the MASTER set. Contains everything.
    delete_samples: contains everything in Insert, just shuffled.
    """

    # First, we can just generate insert_samples by recycling our generation function from before.
    insert_samples = generateRandomSamples(stop)
    search_samples = []

    # Now we'll trace the benchmark cycle to produce the search samples.
    # Each time a benchmarked insert is about to happen (i.e. bm_start + k*bm_interval), we'll be searching for
    # bm_length items randomly chosen from the set of items inserted so far. So we'll expand our search window
    # within insert_samples each time we reach another benchmarking start point.

    # The range(start, stop) in search_samples that we're going to be adding.
    search_start_index = 0
    search_stop_index = bm_length

    # The simulated insert_index value, i.e. the index of the next item to be inserted.
    insert_index = bm_start
    final_stop_index = (((stop - bm_start) // bm_interval) + 1) * bm_length
    while search_start_index < final_stop_index:

        # Imagining we've just inserted up through insert_index...
        print("Choosing search samples {} up to {}".format(search_start_index, search_stop_index))
        search_samples += random.sample(insert_samples[0:insert_index], bm_length)

        # Now we'll increment our search indices.
        search_start_index = search_stop_index
        search_stop_index += bm_length
        insert_index += bm_interval

    # We'll generate delete_samples at the end with a simple random sampling.
    print("Choosing delete samples by randomly sampling insert list")
    delete_samples = random.sample(insert_samples, len(insert_samples))

    return (search_samples, insert_samples, delete_samples)


def generateRandomOperationSequence(size=STOP):
    """Generates a sequence of random operations according to probabilities set in the global configuration (unless
    overridden by options passed as arguments). The returned list is compatible with MixedSIDBenchmarkPlot."""


# ===================================
# SECTION: Graph generation functions
# ===================================


def graph(
        filename,
        functions,
        samples,
        startindex=START,
        stopindex=STOP,
        bm_startindex=BENCHMARK_START,
        bm_length=BENCHMARK_LENGTH,
        bm_interval=BENCHMARK_INTERVAL,
        repeat=REPEAT,
        xlabel=XLABEL,
        ylabel=YLABEL,
        title=""
):
    """Creates and runs a PgfPlot sequence with the given settings, using the benchmarking constants declared above.

    All parameters are passed to PgfPlot(). See that method for documentation. Runs benchmark synchronously; blocks
    until the benchmark is done.

    No return value."""

    if DATA_SETS_TO_PRODUCE > 1:
        for i in range(1, DATA_SETS_TO_PRODUCE + 1):
            PgfPlot(
                # Split filename to add _1, _2, _3, etc.
                filename=filename[0:-4] + str(i) + filename[-4:],
                functions=functions,
                samples=samples,
                startindex=startindex,
                stopindex=stopindex,
                bm_startindex=bm_startindex,
                bm_length=bm_length,
                bm_interval=bm_interval,
                repeat=repeat,
                combine_method=COMBINE_METHOD,
                xlabel=xlabel,
                ylabel=ylabel,
                title=title,
            ).runAndWrite()

    else:
        PgfPlot(
            filename=filename,
            functions=functions,
            samples=samples,
            startindex=startindex,
            stopindex=stopindex,
            bm_startindex=bm_startindex,
            bm_length=bm_length,
            bm_interval=bm_interval,
            repeat=repeat,
            combine_method=COMBINE_METHOD,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
        ).runAndWrite()


def graphSID(
        search_filename,
        insert_filename,
        delete_filename,
        searches,
        inserts,
        deletes,
        search_samples,
        insert_samples,
        delete_samples,
        stopindex=STOP,
        bm_startindex=BENCHMARK_START,
        bm_length=BENCHMARK_LENGTH,
        bm_interval=BENCHMARK_INTERVAL,
        xlabel=XLABEL,
        ylabel=YLABEL,
        title=""
):
    """Creates and runs a SIDGraphSet sequence with the given settings, using the benchmarking constants declared above.

    All parameters are passed to SIDGraphSet(). See that method for documentation. Runs benchmarks synchronously; blocks
    until the benchmarks are done.

    No return value."""

    if DATA_SETS_TO_PRODUCE > 1:
        for i in range(1, DATA_SETS_TO_PRODUCE + 1):
            SIDGraphSet(
                # Split filename to add _1, _2, _3, etc.
                search_filename=search_filename[0:-4] + str(i) + search_filename[-4:],
                insert_filename=insert_filename[0:-4] + str(i) + insert_filename[-4:],
                delete_filename=delete_filename[0:-4] + str(i) + delete_filename[-4:],
                searches=searches,
                inserts=inserts,
                deletes=deletes,
                search_samples=search_samples,
                insert_samples=insert_samples,
                delete_samples=delete_samples,
                stop=stopindex,
                bm_start=bm_startindex,
                bm_length=bm_length,
                bm_interval=bm_interval,
                xlabel=xlabel,
                ylabel=ylabel,
                title=title,
            )
    else:
        SIDGraphSet(
            search_filename=search_filename,
            insert_filename=insert_filename,
            delete_filename=delete_filename,
            searches=searches,
            inserts=inserts,
            deletes=deletes,
            search_samples=search_samples,
            insert_samples=insert_samples,
            delete_samples=delete_samples,
            stop=stopindex,
            bm_start=bm_startindex,
            bm_length=bm_length,
            bm_interval=bm_interval,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
        )


# ==========================
# SECTION: Graph definitions
# ==========================


def testPgfPlot():
    # Create data structures
    bst = BinarySearchTree()
    mylist = []

    # Create samples
    inputs = generateRandomSamples(STOP - START)

    graph(
        "plots/testpgfplot.tex",
        [bst.insert, mylist.append],
        inputs,
        xlabel="TEST X LABEL",
        ylabel="TEST Y LABEL",
        title="TEST TITLE",
    )

def randomAllMiniscule():
    """Performs a miniscule random data test on ALL data structures under consideration."""

    # Initialize data structures
    bst = BinarySearchTree()
    pyskip = PySkip()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Custom benchmarking parameters
    stop = 240
    bm_start = 0
    bm_length = 10
    bm_interval = 40

    # Final setup, and invocation.
    filename = "plots/randomAllMiniscule.tex"
    functions = \
        [bst.insert, pyskip.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.add]
    samples = generateRandomSamples(stop)
    title = "Insert: All Data Structures, Random Input (Miniscule Data Set)"
    graph(
        filename,
        functions,
        samples,
        title=title,
        stopindex=stop,
        bm_startindex=bm_start,
        bm_interval=bm_interval,
        bm_length=bm_length,
        repeat=1
    )


def randomAllTiny():
    """Performs a tiny random data test on ALL data structures under consideration."""

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()

    # Custom benchmarking parameters
    stop = 1010
    bm_start = 100
    bm_length = 10
    bm_interval = 50

    # Final setup, and invocation.
    filename = "plots/randomAllTiny.tex"
    functions = [bst.insert, stromberg_treap.insert]
    samples = generateRandomSamples(stop)
    title = "Insert: All Data Structures, Random Input (Tiny Data Set)"
    graph(
        filename,
        functions,
        samples,
        title=title,
        stopindex=stop,
        bm_startindex=bm_start,
        bm_interval=bm_interval,
        bm_length=bm_length,
        repeat=1
    )


def randomAllTinyRepeat():
    """Performs a tiny random data test on ALL data structures under consideration."""

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()

    # Custom benchmarking parameters
    stop = 1010
    bm_start = 100
    bm_length = 10
    bm_interval = 50

    # Final setup, and invocation.
    filename = "plots/randomAllTinyRepeat.tex"
    functions = [bst.insert, stromberg_treap.insert]
    samples = generateRandomSamples(stop)
    title = "Insert: All Data Structures, Random Input (Tiny Data Set) - Median of 11 runs"
    graph(
        filename,
        functions,
        samples,
        title=title,
        stopindex=stop,
        bm_startindex=bm_start,
        bm_interval=bm_interval,
        bm_length=bm_length,
        repeat=11
    )


def randomAllSmall():
    """Performs a small random data test on ALL data structures under consideration."""

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Custom benchmarking parameters
    stop = 5200
    bm_start = 200
    bm_length = 20
    bm_interval = 200

    # Final setup, and invocation.
    filename = "plots/randomAllSmall.tex"
    functions = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.add]
    samples = generateRandomSamples(stop)
    title = "Insert: All Data Structures, Random Input (Small Data Set)"
    graph(
        filename,
        functions,
        samples,
        title=title,
        stopindex=stop,
        bm_startindex=bm_start,
        bm_interval=bm_interval,
        bm_length=bm_length,
        repeat=1
    )


def insertRandom():
    """Performs a small random data test on ALL data structures under consideration."""

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Final setup, and invocation.
    filename = "plots/insertRandom.tex"
    functions = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.add]
    samples = generateRandomSamples(SAMPLE_SIZE)
    title = "Insert: Random Input"
    graph(
        filename,
        functions,
        samples,
        title=title
    )


def testRandomSID():
    # Initialize data structures.
    bst = BinarySearchTree()

    # Generate sample sets:
    (s, i, d) = generateRandomSIDSampleSet(210, 40, 10, 40)

    bm = SIDBenchmark(
        bst.search,
        bst.insert,
        bst.delete,
        s,
        i,
        d,
        # STOP,
        210,
        # BENCHMARK_START,
        40,
        # BENCHMARK_LENGTH,
        10,
        # BENCHMARK_INTERVAL
        40
    )

    print("\nSearch plot:")
    print(bm.search_plot.coordinates)

    print("\nInsert plot:")
    print(bm.insert_plot.coordinates)

    print("\nDelete plot:")
    print(bm.delete_plot.coordinates)


def testGenerateRandomSIDSampleSet():
    (s, i, d) = generateRandomSIDSampleSet(12, 3, 3, 3)
    print("insert_samples = {}".format(i))
    print("search_samples = {}".format(s))
    print("delete_samples = {}".format(d))


def randomSID():
    """Performs a full search, insert, and delete benchmark set on randomized input data."""

    (search_samples, insert_samples, delete_samples) = generateRandomSIDSampleSet()  # 210, 40, 10, 40)

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Final setup, and invocation.
    base_filename = "plots/random.tex"
    search_filename = base_filename[0:-4] + "_search" + base_filename[-4:]
    insert_filename = base_filename[0:-4] + "_insert" + base_filename[-4:]
    delete_filename = base_filename[0:-4] + "_delete" + base_filename[-4:]
    searches = \
        [bst.search, stromberg_treap.get_key, jenks_treap.__getitem__, pyskiplist.search, redblacktree.find_node]
    inserts = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.add]
    deletes = \
        [bst.delete, stromberg_treap.remove, jenks_treap.__delitem__, pyskiplist.remove, redblacktree.remove]
    title = "Random Input"
    graphSID(
        search_filename,
        insert_filename,
        delete_filename,
        searches,
        inserts,
        deletes,
        search_samples,
        insert_samples,
        delete_samples,
        # 210,
        # 40,
        # 10,
        # 40,
        title=title
    )


def worstCaseSID():
    """Performs a full search, insert, and delete benchmark set on all data structures using the worst-case inputs
    for binary search trees."""

    # Custom test parameters, because a million items will just take eons.
    stop = 10000
    bm_start = 500
    bm_length = 100
    bm_interval = 500

    # Worst-case insert: all increasing.
    insert_samples = list(range(stop))

    # Worst-case delete: always the leaf in our worst-case structure.
    delete_samples = insert_samples[:]
    delete_samples.reverse()

    # Worst-case search: search for the last bm_length elements in our worst-case structure. But this is harder
    # to create since it only does a search at our various intervals.
    search_samples = []
    current = bm_start
    while current < stop:
        search_samples += list(range(current - bm_length, current))
        current = min(stop, current + bm_interval)

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Final setup, and invocation.
    base_filename = "plots/worstCase.tex"
    search_filename = base_filename[0:-4] + "_search" + base_filename[-4:]
    insert_filename = base_filename[0:-4] + "_insert" + base_filename[-4:]
    delete_filename = base_filename[0:-4] + "_delete" + base_filename[-4:]
    searches = \
        [
            bst.search,
            stromberg_treap.get_key,
            jenks_treap.__getitem__,
            pyskiplist.search,
            redblacktree.find_node
        ]
    inserts = \
        [
            bst.insert,
            stromberg_treap.insert,
            jenks_treap.insert,
            pyskiplist.insert,
            redblacktree.add
        ]
    deletes = \
        [
            bst.delete,
            stromberg_treap.remove,
            jenks_treap.__delitem__,
            pyskiplist.remove,
            redblacktree.remove
        ]
    title = "Worst-Case Input"
    graphSID(
        search_filename,
        insert_filename,
        delete_filename,
        searches,
        inserts,
        deletes,
        search_samples,
        insert_samples,
        delete_samples,
        stop,
        bm_start,
        bm_length,
        bm_interval,
        title=title
    )


def worstCaseSIDNoBST():
    """Performs a full search, insert, and delete benchmark set on all data structures using the worst-case inputs
    for binary search trees."""

    # Worst-case insert: all increasing.
    insert_samples = list(range(STOP))

    # Worst-case delete: always the leaf in our worst-case structure.
    delete_samples = insert_samples[:]
    delete_samples.reverse()

    # Worst-case search: search for the last bm_length elements in our worst-case structure. But this is harder
    # to create since it only does a search at our various intervals.
    search_samples = []
    current = BENCHMARK_START
    while current < STOP:
        search_samples += list(range(current - BENCHMARK_LENGTH, current))
        current = min(STOP, current + BENCHMARK_INTERVAL)

    # Initialize data structures
    # bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()
    # avltree = AVLTree()

    # Final setup, and invocation.
    base_filename = "plots/worstCaseNoBST.tex"
    search_filename = base_filename[0:-4] + "_search" + base_filename[-4:]
    insert_filename = base_filename[0:-4] + "_insert" + base_filename[-4:]
    delete_filename = base_filename[0:-4] + "_delete" + base_filename[-4:]
    searches = \
        [
            # bst.search,
            stromberg_treap.get_key,
            jenks_treap.__getitem__,
            pyskiplist.search,
            redblacktree.find_node
        ]
    inserts = \
        [
            # bst.insert,
            stromberg_treap.insert,
            jenks_treap.insert,
            pyskiplist.insert,
            redblacktree.add
        ]
    deletes = \
        [
            # bst.delete,
            stromberg_treap.remove,
            jenks_treap.__delitem__,
            pyskiplist.remove,
            redblacktree.remove
        ]
    title = "Worst-Case Input"
    graphSID(
        search_filename,
        insert_filename,
        delete_filename,
        searches,
        inserts,
        deletes,
        search_samples,
        insert_samples,
        delete_samples,
        title=title
    )


def testMixedSIDPlotSizes():
    """Runs a small test that inserts and deletes between benchmarksexpects known values.

    The operation sequence is as follows:
        1. Insert up to first benchmark.
        2. Search through first benchmark.
        3. Search up to second benchmark.
        4. Insert through second benchmark.
        5. Search up to third benchmark.
        6. Delete through third benchmark.
        7. Search up to fourth benchmark.
        8. Insert and delete in equal numbers through fourth benchmark.

    Expected values are thus easily determined, I expect a specific plot in return.

    For simplicity, the operation between benchmarks is always search, so we don't have to simulate it here at all."""

    # Our printed expected values.
    expected = []

    # Convenience locals
    s = [(MixedSIDBenchmarkPlot.SEARCH, 0)]
    i = [(MixedSIDBenchmarkPlot.INSERT, 0)]
    d = [(MixedSIDBenchmarkPlot.DELETE, 0)]

    # Test parameters
    bm_start = 4
    bm_length = 4
    bm_interval = 8

    # Get us to the first benchmark
    ops = i * bm_start
    size = bm_start
    index = bm_start

    # Run the first simulated benchmark: search.
    expected.append((index, size))
    ops += s * bm_length
    # size does not change.

    # Fast forward
    index += bm_interval
    ops += s * (bm_interval - bm_length)

    # Run the second simulated benchmark: insert.
    expected.append(
        (index,
         statistics.median(list(range(
             size + 1,
             size + bm_length + 1
         ))))
    )
    ops += i * bm_length
    size += bm_length

    # Fast forward
    index += bm_interval
    ops += s * (bm_interval - bm_length)

    # Run the third simulated benchmark: delete.
    expected.append(
        (index,
         statistics.median(list(range(
             size - 1,
             size - bm_length - 1,
             -1
         ))))
    )
    ops += d * bm_length
    size -= bm_length

    # Fast forward
    index += bm_interval
    ops += s * (bm_interval - bm_length)

    # Run the first simulated benchmark: insert and delete equally.
    expected += (index, size)
    ops += (i + d) * (bm_length // 2)
    # size does not change.

    # Now, run the real simulation.
    sim_plot = MixedSIDBenchmarkPlot.plotSizes(ops, bm_start, bm_length, bm_interval)

    # And just for kicks, run the actual benchmark on these operations.
    bst = BinarySearchTree()
    real_plot = MixedSIDBenchmarkPlot(ops, bst.search, bst.insert, bst.delete, bm_start, bm_length, bm_interval)

    # Print for comparison.
    print("MixedSIDBenchmarkPlot test:")
    print("\t operations: " + str(ops))
    print("\tPlease hand-check that the following match:")
    print("\t\t" + str(expected))
    print("\t\t" + str(sim_plot.coordinates))
    print("\tReal benchmark's output:")
    print("\t\t" + str(real_plot.coordinates))


# ==========================
# SECTION: Graph invocations
# ==========================


# testPgfPlot()
# randomAllMiniscule()
# randomAllTiny()
# randomAllTinyRepeat()
# randomAllSmall()
# insertRandom()
# testGenerateRandomSIDSampleSet()
# testRandomSID()
# randomSID()
# worstCaseSID()
# worstCaseSIDNoBST()
testMixedSIDPlotSizes()
