import random
import sys
import statistics
from datastructures.binarysearchtree import BinarySearchTree
from pgfplot import PgfPlot

# Constants defining benchmark behavior. See BenchmarkPlot in plot.py for details.
START = 0
BENCHMARK_START = 100000
BENCHMARK_LENGTH = 1000
BENCHMARK_INTERVAL = 20000
STOP = BENCHMARK_START * 10 + BENCHMARK_LENGTH
REPEAT = 1
COMBINE_METHOD = statistics.median


def generateRandomSamples(n, min=0, max=sys.maxsize):
    """Returns an n-sized array populated with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
    array = [0] * n
    for i in range(n):
        array[i] = random.randrange(min, max+1)
    return array


def graph(filename, functions, samples, xlabel="", ylabel="", title="", caption=""):
    """Creates and runs a PgfPlot sequence with the given settings, using the benchmarking constants declared above.

    All parameters are passed to PgfPlot(). See that method for documentation. Runs benchmark synchronously; blocks
    until the benchmark is done.

    No return value."""

    PgfPlot(
        filename=filename,
        functions=functions,
        samples=samples,
        startindex=START,
        stopindex=STOP,
        bm_startindex=BENCHMARK_START,
        bm_length=BENCHMARK_LENGTH,
        bm_interval=BENCHMARK_INTERVAL,
        repeat=REPEAT,
        combine_method=COMBINE_METHOD,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        caption=caption
    ).run()

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
        "TEST X LABEL",
        "TEST Y LABEL",
        "TEST TITLE",
        "TEST CAPTION"
    )

testPgfPlot()

