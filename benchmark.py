import timeit
import random
import sys
from binarysearchtree import BinarySearchTree


class PgfPlot:
    """Represents a LaTeX pgfplots graph generated from benchmarking algorithms.

    The typical workflow might look something like this:
    1. Initialize the PgfPlot
    2. Add Plots
    3. Generate"""

    def __init__(
            self,
            xlabel="",
            ylabel="",
            title="",
            caption="",
    ):
        """Initializes all options of a BenchmarkGraph:

        inputSet: the data to be used in the benchmarks, in the order in which they should be used.
        xlabel: the x-axis label, e.g. \begin{axis}[xlabel={foo}]
        ylabel: the y-axis label, e.g. \begin{axis}[xlabel={foo}]
        title: the graph title, e.g. \begin{axis}[title={foo}]
        caption: the figure caption, e.g. \caption{foo}"""
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.caption = caption
        self.plots = []

    def addPlot(self, plot):
        """Adds plot to the graph."""
        self.plots.append(plot)

    # TODO Write generate method.


class Plot:
    """Represents one Plot, e.g. one line, curve, etc., of a LaTeX PgfPlots graph."""

    def __init__(self):
        self.coordinates = []

    def plotPoint(self, x, y):
        """Records (x, y) as a point on the plot."""
        self.coordinates.append((x, y))

    # TODO Write generate method


def benchmark(function, samples, start, stop):
    """Returns the total time used by calling function(x) on every x in sample with indices in range(start, stop)."""
    return timeit.timeit(stmt=lambda: _benchmarkRun(function, samples, start, stop), number=1)


def _benchmarkRun(function, samples, start, stop):
    """Runs function(x) on every x in sample with indices in range(start, stop)."""
    for i in range(start, stop):
        function(samples[i])


def generateInput(n, min=0, max=sys.maxsize):
    """Returns an n-sized array and populates it with random values in the range of [min, max]."""
    array = [0] * n
    for i in range(n):
        array[i] = random.randrange(min, max+1)
    return array


def plotBenchmarks(
        function,
        samples,
        start,
        stop,
        benchmark_start,
        benchmark_length,
        benchmark_interval
):
    """Returns a Plot containing the results of a full suite of benchmarks.

    Starting with samples[start], plotBenchmarks will call function(x), passing subsequent items from samples as x.
    When the index reaches benchmark_start, it will time the function(x) calls for benchmark_length indices and record
    that as a single data point on the Plot. Then, it will proceed until it reaches index
    benchmark_start + benchmark_interval, where it will create another data point for the plot.

    For instance:

    plotBenchmarks(
        function=lambda x: mylist.append(x),
        samples=list(range(10000),
        start=0,
        stop=10000,
        benchmark_start=0,
        benchmark_length=100,
        benchmark_interval=1000
    )

    will produce a plot with benchmark times for the following ranges:
    [0, 99]
    [1000, 1099]
    [2000, 2099]
    [3000, 3099]
    ...
    [9000, 9099]

    In between these ranges, it will simply call function without timing the operation.
    """

    if benchmark_start < start:
        raise ValueError("benchmark_start must be equal to or greater than start")

    if benchmark_start > stop:
        raise ValueError("benchmark_start must be less than or equal to stop")

    # Jog our way to the first benchmark
    for i in range(0, benchmark_start):
        function(samples[i])

    # We'll cycle, now, from benchmarking to non-benchmarking and back, until we reach stop.
    # For the remainder of the benchmark cycle, we will use next_benchmark to track when to start a benchmark
    # and p and q to represent the start and end of a range that we're calculating.
    next_benchmark = benchmark_start
    p = benchmark_start
    q = p
    plot = Plot()
    while q < stop:
        # Don't overshoot stop when benchmarking.
        q = min(p + benchmark_length, stop)
        time = benchmark(function, samples, p, q)
        plot.plotPoint(p, time)
        next_benchmark = p + benchmark_interval

        # Then, advance to the next benchmark
        p = q + 1
        q = min(next_benchmark, stop)
        for i in range(p, q):
            function(samples[i])

    return plot

START = 0
BM_START = 10000
BM_LENGTH = 1000
BM_INTERVAL = BM_START
STOP = BM_START * 10 + BM_LENGTH

bst = BinarySearchTree()
inputs = generateInput(STOP - START)
plot = plotBenchmarks(
    function=lambda x: bst.insert(x),
    samples=inputs,
    start=START,
    stop=STOP,
    benchmark_start=BM_START,
    benchmark_length=BM_LENGTH,
    benchmark_interval=BM_INTERVAL
)
print(plot.coordinates)

# for i in range(0, TIMES):
#     print(timeit.timeit(lambda: insert(bst, inputs, SAMPLES*i, SAMPLES*(i+1)), number=1))
