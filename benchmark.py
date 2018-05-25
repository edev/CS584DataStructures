import random
import sys
import statistics
from datastructures.binarysearchtree import BinarySearchTree
from pgfplot import PgfPlot


def generateInput(n, min=0, max=sys.maxsize):
    """Returns an n-sized array and populates it with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
    array = [0] * n
    for i in range(n):
        array[i] = random.randrange(min, max+1)
    return array


def testPfgPlot():
    # Create data structures
    bst = BinarySearchTree()
    mylist = []

    # Create samples
    START = 0
    BM_START = 10000
    BM_LENGTH = 1000
    BM_INTERVAL = BM_START
    STOP = BM_START * 10 + BM_LENGTH
    PASSES = 3
    inputs = generateInput(STOP - START)

    testpgfplot = PgfPlot(
        filename="plots/testpgfplot.tex",
        functions=[bst.insert, mylist.append],
        samples=inputs,
        startindex=START,
        stopindex=STOP,
        bm_startindex=BM_START,
        bm_length=BM_LENGTH,
        bm_interval=BM_INTERVAL,
        repeat=PASSES,
        combine_method=statistics.median,
        xlabel="TEST X LABEL",
        ylabel="TEST Y LABEL",
        title="TEST TITLE",
        caption="TEST CAPTION"
    )

    # Do the benchmark
    testpgfplot.run()


testPfgPlot()

# def testWriteBenchmark():
#     START = 0
#     BM_START = 10000
#     BM_LENGTH = 1000
#     BM_INTERVAL = BM_START
#     STOP = BM_START * 10 + BM_LENGTH
#     PASSES = 3
#
#     bst = BinarySearchTree()
#     inputs = [0] * PASSES
#     for i in range(PASSES):
#         inputs[i] = generateInput(STOP - START)
#     plot = plotBenchmarksMultipass(
#         function=lambda x: bst.insert(x),
#         samples=inputs,
#         start=START,
#         stop=STOP,
#         benchmark_start=BM_START,
#         benchmark_length=BM_LENGTH,
#         benchmark_interval=BM_INTERVAL
#     )
#     figure = PgfPlot("Data structure size",
#                      "Elapsed time (seconds)",
#                      "BST on Randomized Input",
#                      "Binary Search Tree - Randomized Input Set, 3 Passes")
#     figure.write("plots/testWriteBenchmark.tex")


# for i in range(0, TIMES):
#     print(timeit.timeit(lambda: insert(bst, inputs, SAMPLES*i, SAMPLES*(i+1)), number=1))

# doPlotBenchmarksMultipass()

# print("testWriteBenchmark started at: " + time.asctime(time.localtime(time.time())))
# testWriteBenchmark()
# print("Completed at: " + time.asctime(time.localtime(time.time())) + ". Starting raw insertion.")

# inputs = [[]] * 3
# for i in range(3):
#     inputs[i] = generateInput(101000)

# for i in range(3):
# bst = BinarySearchTree()
# plotBenchmarksMultipass(bst.insert, inputs, 0, len(inputs[i]), 1000, 1000, 1000) # 3-pass benchmarks, again, fast.
    # print("BST insertion (set {}) started at {}".format(i+1, time.asctime(time.localtime(time.time()))))
    # plotBenchmarks(bst.insert, inputs[i], 0, len(inputs[i]), 1000, 1000, 1000) # Series of benchmarks - runs fairly fast
    # benchmark(bst.insert, inputs[i], 0, len(inputs[i])) # Single benchmark - runs fast.
    # for j in range(len(inputs[i])):
        # bst.insert(inputs[i][j]) # Raw insertion - runs fast.
