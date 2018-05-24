import timeit
import random
import sys
import statistics
from binarysearchtree import BinarySearchTree
import trender
import time


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
            template = "figure.template.tex"
    ):
        """Initializes all options of a BenchmarkGraph:

        xlabel: the x-axis label, e.g. \begin{axis}[xlabel={foo}]
        ylabel: the y-axis label, e.g. \begin{axis}[xlabel={foo}]
        title: the graph title, e.g. \begin{axis}[title={foo}]
        caption: the figure caption, e.g. \caption{foo}
        template: the name of the template file to use."""

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.caption = caption
        self.plots = []

        with open(template, 'r') as f:
            self.template = trender.TRender(f.read())

    def addPlot(self, plot):
        """Adds plot to the graph."""
        self.plots.append(plot)

    def write(self, filename):
        """Writes the LaTeX Figure object to the specified file.

        filename: the filename to use when writing the results to disk."""

        # First, prepare the plots.
        plots = ""
        for plot in self.plots:
            plots += plot.generate()
        # Then, strip off the final "\n".
        plots = plots[0:-2]

        # Next, render the template.
        output = self.template.render({
            "xlabel": self.xlabel,
            "ylabel": self.ylabel,
            "title": self.title,
            "caption": self.caption,
            "plots": plots
        })

        # Finally, write the file.
        with open(filename, "w") as f:
            f.write(output)

class Plot:
    """Represents one Plot, e.g. one line, curve, etc., of a LaTeX PgfPlots graph."""

    def __init__(self):
        self.coordinates = []

    def plotPoint(self, x, y):
        """Records (x, y) as a point on the plot."""
        self.coordinates.append((x, y))

    def generate(self, base_indentation=2) -> str:
        """Returns a LaTeX string representation of the Plot, in the form of an addplot object.

        base_inedntation: the number of tabs to insert before the addplot tag.
            Subsequent lines will be indented appropriately."""
        tabs = "\t" * (base_indentation + 1)
        output = "\t" * base_indentation + "\\addplot coordinates {\n"
        for (x, y) in self.coordinates:
            output += tabs + "({}, {})\n".format(x, y)
        output += "\t" * base_indentation + "};\n"
        return output


def benchmark(function, samples, start, stop):
    """Returns the total time used by calling function(x) on every x in sample with indices in range(start, stop)."""
    print("Starting benchmark on sample range: [{}, {})".format(start, stop))
    return timeit.timeit(stmt=lambda: _benchmarkRun(function, samples, start, stop), number=1)


def _benchmarkRun(function, samples, start, stop):
    """Runs function(x) on every x in sample with indices in range(start, stop)."""
    for i in range(start, stop):
        function(samples[i])


def generateInput(n, min=0, max=sys.maxsize):
    """Returns an n-sized array and populates it with random values in the range of [min, max]."""

    print("Generating random array of size {}".format(n))
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
        benchmark_interval,
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


def plotBenchmarksMultipass(
        function,
        samples,
        start,
        stop,
        benchmark_start,
        benchmark_length,
        benchmark_interval,
        combine_method=statistics.median
):
    """Calls plotBenchmarks on multiple samples, then combines data points to form a single plot.

    samples: a list of sample lists, where each sample list will be passed into plotBenchmarks as sample.
    combine_method: "median" or "average".

    After running each sample list through plotBenchmarks, plotBenchmarksMultiplass will create a list of y-values
    for each x-value (e.g. [1.10003, 1.1405, 0.981] for some x-value if samples has 3 sample sets) and produce a
    final y-value for that x-value by calling combine_method on that list. The statistics package has good, common
    choices like mean and various medians.

    Finally, it will return one plot containing all such resulting coordinates."""

    if not isinstance(samples[0], list):
        raise TypeError("samples must be a list of lists.")

    plots = [Plot()] * len(samples)

    for i in range(len(samples)):
        plots[i] = plotBenchmarks(
            function,
            samples[i],
            start,
            stop,
            benchmark_start,
            benchmark_length,
            benchmark_interval
        )

    final_plot = Plot()
    num_pluts = len(plots)
    for j in range(len(plots[0].coordinates)):
        yvalues = [0] * num_pluts
        for i in range(num_pluts):
            yvalues[i] = plots[i].coordinates[j][1]
        final_plot.plotPoint(plots[0].coordinates[j][0], combine_method(yvalues))

    # PURELY FOR TESTING
    for i in range(len(plots)):
        print(plots[i].coordinates)
    return final_plot


def plotBenchmark3(
        function,
        samples,
        start,
        stop,
        benchmark_start,
        benchmark_length,
        benchmark_interval,
        combine_method=statistics.median
):
    """Wrapper around plotBenchmarkMultipass to make it easier to run the same sample 3 times.

    Duplicates the sample list 3 times and passes it into plotBenchmarkMultipass, returning the result."""

    return plotBenchmarksMultipass(
        function,
        samples * 3,
        start,
        stop,
        benchmark_start,
        benchmark_length,
        benchmark_interval,
        combine_method
    )


def doPlotBenchmarks():
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


def doPlotBenchmarksMultipass():
    START = 0
    BM_START = 10000
    BM_LENGTH = 1000
    BM_INTERVAL = BM_START
    STOP = BM_START * 10 + BM_LENGTH
    PASSES = 3

    bst = BinarySearchTree()
    inputs = [0] * PASSES
    for i in range(PASSES):
        inputs[i] = generateInput(STOP - START)
    plot = plotBenchmarksMultipass(
        function=lambda x: bst.insert(x),
        samples=inputs,
        start=START,
        stop=STOP,
        benchmark_start=BM_START,
        benchmark_length=BM_LENGTH,
        benchmark_interval=BM_INTERVAL
    )
    print(plot.coordinates)


def testPfgPlot():
    testpfgplot = PgfPlot(
        xlabel="TEST X LABEL",
        ylabel="TEST Y LABEL",
        title="TEST TITLE",
        caption="TEST CAPTION"
    )
    testplot = Plot()
    testplot.plotPoint(1, 2)
    testplot.plotPoint(3, 4)
    testplot.plotPoint(5, 6)
    testpfgplot.addPlot(testplot)
    testplot2 = Plot()
    testpfgplot.addPlot(testplot2)
    testplot2.plotPoint(1, 5)
    testplot2.plotPoint(2, 6)
    testplot2.plotPoint(3, 7)
    testplot2.plotPoint(4, 8)
    testplot2.plotPoint(5, 9)
    testpfgplot.write("plots/testpfgplot.tex")


def testWriteBenchmark():
    START = 0
    BM_START = 10000
    BM_LENGTH = 1000
    BM_INTERVAL = BM_START
    STOP = BM_START * 10 + BM_LENGTH
    PASSES = 3

    bst = BinarySearchTree()
    inputs = [0] * PASSES
    for i in range(PASSES):
        inputs[i] = generateInput(STOP - START)
    plot = plotBenchmarksMultipass(
        function=lambda x: bst.insert(x),
        samples=inputs,
        start=START,
        stop=STOP,
        benchmark_start=BM_START,
        benchmark_length=BM_LENGTH,
        benchmark_interval=BM_INTERVAL
    )
    figure = PgfPlot("Data structure size",
                     "Elapsed time (seconds)",
                     "BST on Randomized Input",
                     "Binary Search Tree - Randomized Input Set, 3 Passes")
    figure.write("plots/testWriteBenchmark.tex")


# for i in range(0, TIMES):
#     print(timeit.timeit(lambda: insert(bst, inputs, SAMPLES*i, SAMPLES*(i+1)), number=1))

# doPlotBenchmarksMultipass()

print("testWriteBenchmark started at: " + time.asctime(time.localtime(time.time())))
testWriteBenchmark()
print("Completed at: " + time.asctime(time.localtime(time.time())) + ". Starting raw insertion.")

inputs = [0] * 3
for i in range(3):
    inputs[i] = generateInput(101000)
for i in range(3):
    bst = BinarySearchTree()
    for j in range(len(inputs)):
        bst.insert(inputs[j])
