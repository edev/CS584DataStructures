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
        # coord_index is the index into coordinates where the result should be stored.
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


class SIDBenchmark:
    """Performs similar functions to BenchmarkPlot, except that it specifically calls a sequence of search, insert,
    and delete operations and produces Plots corresponding to these operations."""

    def __init__(
            self,
            search,
            insert,
            delete,
            search_samples,
            insert_samples,
            delete_samples,
            stop,
            bm_start,
            bm_length,
            bm_interval,
    ):
        """
        Instantiates a Plot containing the results of a full suite of search, insert, and delete benchmarks.
        Runs these benchmarks immediately and synchronously. Saves the results as instance variables. Note that this
        benchmark differs substantially from BenchmarkPlot, even though its interface is similar!

        The benchmark accepts 3 sample sets and maintain 3 indices: one apiece for search, index, and delete. The
        data structure on which search, insert, and delete are called is presumed to be empty prior to this benchmark;
        the plot points count from 0 elements. Each index starts at 0.

        The sample sets should have the following minimum sizes:
            len(search_samples) >= the number of searches requested (likely bm_length times some integer)
            len(insert_samples) >= stop
            len(delete_samples) >= stop

        The pseudocode is as follows:
            0. Set next_benchmark as bm_start.
            1. Call insert on the items in insert_samples with indices [0, bm_start).
            2. While insert_index < stop:
                a. set last_benchmark as next_benchmark.
                b. Set next_benchmark as min(next_benchmark + bm_interval, stop).
                c. Benchmark: time bm_length searches on items in search_samples[search_index]. Divide the total time by
                    bm_length and save (data structure size, time) as a plot point for insert.
                d. Benchmark: time bm_length inserts on items in insert_samples[insert_index]. Divide the total time by
                    bm_length and save (data structure size before timed insertions, time) as a plot point for insert.
                e. Insert subsequent items from insert_samples, incrementing insert_index, until
                    insert_index == next_benchmark. These insertions are not timed.
            3. Set next_benchmark = last_benchmark + bm_length.
            4. While data structure size > bm_start:
                a. Delete items from delete_samples[delete_index], incrementing delete_index, until
                    data structure size == next_benchmark.
                b. Benchmark: time bm_length deletions on items in delete_samples[delete_index], incrementing
                    delete_index each time. Divide the total time by bm_length and save
                    (data structure size after timed deletions, time) as a plot point for delete.
                c. Decrease next_benchmark by bm_interval.

        Parameters:
            search: the search function to call.
            insert: the insert function to call.
            delete: the delete function to call.
            search_samples: the samples to search for, in the order in which they should be passed.
            insert_samples: the samples to insert, in the order in which they should be inserted.
            delete_samples: the samples to be deleted, in the order in which they should be deleted.
            stop: the number of items to insert, in total. Ensure that stop <= len(insert_samples).
            bm_start: the index in insert_samples of the first index to benchmark. Assuming the data structure starts
                empty, bm_start is the size of the data structure when the first benchmarks are performed.
            bm_length: the number of items to pass into search, insert, and delete during each benchmark,
                i.e. the sample size. Ensure that bm_length >= bm_start and that search_samples and delete_samples
                have at least bm_length items for each benchmark to be performed.
            bm_interval: the number of elements between one benchmark's beginning and the next, i.e. the increment
                of data structure size between plot points.
        """

        if bm_start < bm_length:
            raise ValueError("bm_start must be no smaller than bm_length.")

        self.search_plot = Plot()
        self.insert_plot = Plot()
        self.delete_plot = Plot()

        self._doBenchmark(
            search,
            insert,
            delete,
            search_samples,
            insert_samples,
            delete_samples,
            stop,
            bm_start,
            bm_length,
            bm_interval,
        )

    def _doBenchmark(
            self,
            search,
            insert,
            delete,
            search_samples,
            insert_samples,
            delete_samples,
            stop,
            bm_start,
            bm_length,
            bm_interval,
     ):
        """Helper function. Performs the benchmark routine described elsewhere."""

        # Initialize indices.
        search_index = insert_index = delete_index = 0

        # 0. Set next_benchmark as bm_start.
        next_benchmark = bm_start

        # 1. Call insert on the items in insert_samples with indices [0, bm_start).
        print("Inserting up to {}".format(bm_start))
        for i in range(0, bm_start):
            insert(insert_samples[insert_index])
            insert_index += 1

        # 2. While insert_index < stop:
        while insert_index < stop:
            # a. set last_benchmark as next_benchmark.
            last_benchmark = next_benchmark

            # b. Set next_benchmark as min(next_benchmark + bm_interval, stop).
            next_benchmark = min(next_benchmark + bm_interval, stop)

            # c. Benchmark: time bm_length searches on items in search_samples[search_index]. Divide the total time by
            #    bm_length and save (data structure size, time) as a plot point for insert.
            print("Benchmarking: search for items {} to {}".format(search_index, search_index + bm_length))
            self.search_plot.plotPoint(
                insert_index,
                Plot.benchmark(
                    search,
                    search_samples,
                    search_index,
                    search_index + bm_length
                )
            )
            search_index += bm_length

            # d. Benchmark: time bm_length inserts on items in insert_samples[insert_index]. Divide the total time by
            #    bm_length and save (data structure size before timed insertions, time) as a plot point for insert.
            print("Benchmarking: insert items {} to {}".format(insert_index, insert_index + bm_length))
            self.insert_plot.plotPoint(
                insert_index,
                Plot.benchmark(
                    insert,
                    insert_samples,
                    insert_index,
                    insert_index + bm_length
                )
            )
            insert_index += bm_length

            # e. Insert subsequent items from insert_samples, incrementing insert_index, until
            #    insert_index == next_benchmark. These insertions are not timed.
            print("Inserting intermediate values up to {}".format(next_benchmark))
            while insert_index < next_benchmark:
                insert(insert_samples[insert_index])
                insert_index += 1

        # 3. Set next_benchmark = last_benchmark + bm_length.
        next_benchmark = last_benchmark + bm_length

        # 4. While data structure size > bm_start:
        # We could reuse insert_index, but this is VASTLY clearer.
        data_structure_size = insert_index
        while data_structure_size > bm_start:
            # a. Delete items from delete_samples[delete_index], incrementing delete_index, until
            #    data structure size == next_benchmark.
            print("Deleting vlues down to {}".format(next_benchmark))
            while data_structure_size > next_benchmark:
                delete(delete_samples[delete_index])
                delete_index += 1
                data_structure_size -= 1

            # b. Benchmark: time bm_length deletions on items in delete_samples[delete_index], incrementing
            #    delete_index each time. Divide the total time by bm_length and save
            #    (data structure size after timed deletions, time) as a plot point for delete.
            print("Benchmarking: delete items {} to {}".format(delete_index, delete_index + bm_length))
            data_structure_size -= bm_length
            self.delete_plot.plotPoint(
                data_structure_size,
                Plot.benchmark(
                    delete,
                    delete_samples,
                    delete_index,
                    delete_index + bm_length
                )
            )
            delete_index += bm_length

            # c. Decrease next_benchmark by bm_interval.
            next_benchmark -= bm_interval
