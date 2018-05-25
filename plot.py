import statistics
import timeit

class Plot:
    """Represents one Plot, e.g. one line, curve, etc., of a LaTeX PgfPlots graph."""

    def __init__(self):
        self.coordinates = []

    def plotPoint(self, x, y):
        """Records (x, y) as a point on the plot."""
        self.coordinates.append((x, y))

    def get_latex(self, base_indentation=2) -> str:
        """Returns a LaTeX string representation of the Plot, in the form of an addplot object.

        base_indentation: the number of tabs to insert before the addplot tag.
            Subsequent lines will be indented appropriately."""
        tabs = "\t" * (base_indentation + 1)
        output = "\t" * base_indentation + "\\addplot coordinates {\n"
        for (x, y) in self.coordinates:
            output += tabs + "({}, {})\n".format(x, y)
        output += "\t" * base_indentation + "};\n"
        return output


class BenchmarkPlot(Plot):
    def __init__(
            self,
            function,
            samples,
            start,
            stop,
            benchmark_start,
            benchmark_length,
            benchmark_interval,
            repeat,
            combine_method
    ):
        """
        Instantiates a Plot containing the results of a full suite of benchmarks. Runs these benchmarks immediately
        and synchronously.

        When repeat == 1:
        Starting with samples[startindex], the benchmark will call function(x), passing subsequent items from samples
        as x. When the index reaches bm_start, it will time the function(x) calls for bm_length indices, divide the
        resulting time by bm_length, and record that time as a single data point on the Plot. Then, it will proceed
        until it reaches index bm_start + bm_interval, where it will create another data point for the plot. It will
        proceed in this way until it reaches stopindex. stopindex will not be included in the benchmark. The value
        of combine_method will be ignored; it may safely be null.

        When repeat > 1:
        The above procedure will be used, except that the entire benchmark will be run repeat times, and the results
        for corresponding plot points will be combined using combine_method. For combine_method, many common choices
        can be found in the statistics module, e.g. statistics.median or statistics.mean. The combined result (e.g.
        the median or mean) will be plotted.

        For instance:

        plotBenchmarks(
            function=lambda x: mylist.append(x),
            samples=list(range(10000)),
            start=0,
            stop=10000,
            benchmark_start=0,
            benchmark_length=100,
            benchmark_interval=1000,
            repeat=1,
            combine_method=null
        )

        will produce a plot with benchmark times for the following ranges:
        [0, 99]
        [1000, 1099]
        [2000, 2099]
        [3000, 3099]
        ...
        [9000, 9099]

        In between these ranges, it will simply call function without timing the operation. This is useful for gathering
        multiple data points on, say, an insertion operation at various intervals throughout a large data set, in order
        to smooth out inaccuracies in the timing data.
        """

        super(BenchmarkPlot, self).__init__()

        if repeat < 0:
            raise ValueError("repeat must be a positive integer.")

        if repeat == 1:
            self.coordinates = self._doBenchmark(
                function,
                samples,
                start,
                stop,
                benchmark_start,
                benchmark_length,
                benchmark_interval
            )
        else:
            runs = [[]] * repeat
            for i in range(repeat):
                runs[i] = self._doBenchmark(
                    function,
                    samples,
                    start,
                    stop,
                    benchmark_start,
                    benchmark_length,
                    benchmark_interval
                )

            self.coordinates = [0] * len(runs[0])
            yvalues = [0] * repeat
            # Loop through each x-value index as j
            for j in range(len(runs[0])):
                # Loop through each run index as i
                for i in range(repeat):
                    # run i, coordinate j, tuple element 1 (y-value).
                    yvalues[i] = runs[i][j][1]
                # Plot the (x, y) pair after combining the y-values.
                self.coordinates[j] = (runs[0][j][0], combine_method(yvalues))

    def _doBenchmark(
            self,
            function,
            samples,
            start,
            stop,
            benchmark_start,
            benchmark_length,
            benchmark_interval,
    ) -> list:
        """Helper function for benchmark(). Returns a list of coordinates containing the results of a single pass of a
        benchmark suite."""

        if benchmark_start < start:
            raise ValueError("benchmark_start must be equal to or greater than start")

        if benchmark_start > stop:
            raise ValueError("benchmark_start must be less than or equal to stop")

        # Prepare the coordinate list.
        coordinates = []

        # Jog our way to the first benchmark
        for i in range(0, benchmark_start):
            function(samples[i])

        # We'll cycle, now, from benchmarking to non-benchmarking and back, until we reach stop.
        # For the remainder of the benchmark cycle, we will use next_benchmark to track when to start a benchmark
        # and p and q to represent the start and end, respectively, of a range that we're calculating.
        # coord_index is the index into coordinates where the result should be stored.
        p = benchmark_start
        while p < stop:
            # Don't overshoot stop when benchmarking.
            q = min(p + benchmark_length, stop)
            time = benchmark(function, samples, p, q)
            coordinates.append((p, time))
            next_benchmark = p + benchmark_interval

            # Then, advance to the next benchmark
            p = q
            q = min(next_benchmark, stop)
            for i in range(p, q):
                function(samples[i])

            # Before looping, update p.
            p = q

        return coordinates


def benchmark(function, samples, start, stop):
    """Returns the total time used by calling function(x) on every x in sample with indices in range(start, stop)."""
    print("Starting benchmark on sample range: [{}, {})".format(start, stop))
    return timeit.timeit(stmt=lambda: _benchmarkRun(function, samples, start, stop), number=1) / (stop - start)


def _benchmarkRun(function, samples, start, stop):
    """Runs function(x) on every x in sample with indices in range(start, stop)."""
    for i in range(start, stop):
        function(samples[i])


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
        samples=list(range(10000)),
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
        p = q
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


# def doPlotBenchmarks():
#     START = 0
#     BM_START = 10000
#     BM_LENGTH = 1000
#     BM_INTERVAL = BM_START
#     STOP = BM_START * 10 + BM_LENGTH
#
#     bst = BinarySearchTree()
#     inputs = generateInput(STOP - START)
#     plot = plotBenchmarks(
#         function=lambda x: bst.insert(x),
#         samples=inputs,
#         start=START,
#         stop=STOP,
#         benchmark_start=BM_START,
#         benchmark_length=BM_LENGTH,
#         benchmark_interval=BM_INTERVAL
#     )
#     print(plot.coordinates)
#
#
# def doPlotBenchmarksMultipass():
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
#     print(plot.coordinates)