import random
import sys
import statistics
from datastructures.binarysearchtree import BinarySearchTree
from datastructures.toastdriven_pyskip import Skiplist as PySkip
from datastructures.stromberg_treap import treap as StrombergTreap
from datastructures.jenks_treap import Treap as JenksTreap
from datastructures.pyskiplist.skiplist import SkipList as PySkipList
from datastructures.redblacktree import RedBlackTree
from pgfplot import PgfPlot
from sidgraphset import SIDGraphSet, SIDBenchmark

# Constants defining benchmark behavior. See BenchmarkPlot in plot.py for details.
START = 0
BENCHMARK_START = 100000
BENCHMARK_LENGTH = 1000
BENCHMARK_INTERVAL = 20000
STOP = BENCHMARK_START * 10 + BENCHMARK_LENGTH
REPEAT = 1
COMBINE_METHOD = statistics.median

# Produce this many graph .tex files for each graph - so you can choose the best data set later in LaTeX.
DATA_SETS_TO_PRODUCE = 10

# Convenience constant for generating samples of the same size as the benchmark
SAMPLE_SIZE = STOP - START

# Constants determining default graph labels. Override in the call to graph() if desired.
XLABEL = "Numer of items in data structure"
YLABEL = "Running time (second)"


def generateRandomSamples(n=SAMPLE_SIZE):
    """Returns an n-sized array populated with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
    return random.sample(list(range(n)), n)
    return array


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
            ).run()

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
        ).run()


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
        for i in range(search_start_index, search_stop_index):
            # Choose a random element from the items that have been chosen so far.
            # TODO Change this whole loop to a random.sample call
            # TODO Make search_samples a list of size final_stop_index
            search_samples.append(random.choice(insert_samples[:insert_index]))

        # Now we'll increment our search indices.
        search_start_index = search_stop_index
        search_stop_index += bm_length
        insert_index += bm_interval

    # We'll generate delete_samples at the end with a simple random sampling.
    print("Choosing delete samples by randomly sampling insert list")
    delete_samples = random.sample(insert_samples, len(insert_samples))

    return (search_samples, insert_samples, delete_samples)


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

    # Custom benchmarking parameters
    stop = 240
    bm_start = 0
    bm_length = 10
    bm_interval = 40

    # Final setup, and invocation.
    filename = "plots/randomAllMiniscule.tex"
    functions = \
        [bst.insert, pyskip.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.insert]
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

    # Custom benchmarking parameters
    stop = 5200
    bm_start = 200
    bm_length = 20
    bm_interval = 200

    # Final setup, and invocation.
    filename = "plots/randomAllSmall.tex"
    functions = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.insert]
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

    # Final setup, and invocation.
    filename = "plots/insertRandom.tex"
    functions = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, redblacktree.insert]
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


def testRandomSIDGraph():
    """Performs a small random data test on all data structures under consideration, for testing."""

    (search_samples, insert_samples, delete_samples) = generateRandomSIDSampleSet(210, 40, 10, 40)

    # Initialize data structures
    bst = BinarySearchTree()
    stromberg_treap = StrombergTreap()
    jenks_treap = JenksTreap()
    pyskiplist = PySkipList()
    redblacktree = RedBlackTree()

    # Final setup, and invocation.
    base_filename = "plots/testRandomSID.tex"
    search_filename = base_filename[0:-4] + "_search" + base_filename[-4:]
    insert_filename = base_filename[0:-4] + "_insert" + base_filename[-4:]
    delete_filename = base_filename[0:-4] + "_delete" + base_filename[-4:]
    searches = \
        [bst.search, stromberg_treap.get_key, jenks_treap.__getitem__, pyskiplist.search, ]#redblacktree.search]
    inserts = \
        [bst.insert, stromberg_treap.insert, jenks_treap.insert, pyskiplist.insert, ]#redblacktree.insert]
    deletes = \
        [bst.delete, stromberg_treap.remove, jenks_treap.__delitem__, pyskiplist.remove, ]#redblacktree.delete]
    title = "Insert: Random Input"
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
        210,
        40,
        10,
        40,
        title=title
    )


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
testRandomSIDGraph()