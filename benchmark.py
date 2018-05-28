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


def generateRandomSamples(n=SAMPLE_SIZE, min=0, max=sys.maxsize):
    """Returns an n-sized array populated with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
    array = [0] * n
    for i in range(n):
        array[i] = random.randrange(min, max+1)
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


# ==========================
# SECTION: Graph invocations
# ==========================


# testPgfPlot()
# randomAllMiniscule()
# randomAllTiny()
# randomAllTinyRepeat()
# randomAllSmall()
insertRandom()
