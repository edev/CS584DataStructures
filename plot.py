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

    @staticmethod
    def benchmark(function, samples, start, stop):
        """Returns the total time used by calling function(x) on every x in sample with indices in range(start, stop)"""
        time = timeit.timeit(stmt=lambda: Plot._benchmarkRun(function, samples, start, stop), number=1)
        time = time / (stop - start)
        return time

    @staticmethod
    def _benchmarkRun(function, samples, start, stop):
        """Runs function(x) on every x in sample with indices in range(start, stop)."""
        for i in range(start, stop):
            function(samples[i])


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
        Starting with samples[start], the benchmark will call function(x), passing subsequent items from samples
        as x. When the index reaches bm_start, it will time the function(x) calls for bm_length indices, divide the
        resulting time by bm_length, and record that time as a single data point on the Plot. Then, it will proceed
        until it reaches index bm_start + bm_interval, where it will create another data point for the plot. It will
        proceed in this way until it reaches stop. stop will not be included in the benchmark. The value
        of combine_method will be ignored; it may safely be null.

        When repeat > 1:
        The above procedure will be used, except that the entire benchmark will be run repeat times, and the results
        for corresponding plot points will be combined using combine_method. For combine_method, many common choices
        can be found in the statistics module, e.g. statistics.median or statistics.mean. The combined result (e.g.
        the median or mean) will be plotted.

        For instance:

        plotBenchmarks(
            function=mylist.append,
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
        p = benchmark_start
        while p < stop:
            # Don't overshoot stop when benchmarking.
            q = min(p + benchmark_length, stop)
            time = Plot.benchmark(function, samples, p, q)
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
