from pgfplot import PgfPlot
from plot import Plot
import statistics


class MixedSIDPgfPlot(PgfPlot):
    """Creates a single graph containing the results of a mixed set of search, insert, and delete operations
    on a set of data structures. Also plots the median data structure size at each plotted x-value."""

    def __init__(
            self,
            filename,
            searches,
            inserts,
            deletes,
            operations, # Known internally as samples, same as PgfPlots.
            bm_startindex,
            bm_length,
            bm_interval,
            xlabel="",
            ylabel="",
            title="",
            template="figure.template.tex",
    ):
        """Configures a series of benchmarks on all the inputs provided and plots them, alongside the size of the data
        structure.

        functions: a list of dictionaries, one per data structure. Each dictionary should be of the following form:
        {MixedSIDBenchmarkPlot.SEARCH: your_search_Function,
         MixedSIDBenchmarkPlot.INSERT: your_insert_function,
         MixedSIDBenchmarkPlot.DELETE: your_delete_function}

        This constructor does not accept the startindex, stopindex, repeat, or combine_method options,
        since they do not apply here.

        operations is a list of operations according to the MixedSIDBenchmark spec.

        All other options are the same as PgfPlots and are directly passed through.
        """

        super(MixedSIDPgfPlot, self).__init__(
            filename,
            searches[:],   # Simply used for generating legend text, in our case. We'll augment this value in run().
            operations,
            0,
            0,
            bm_startindex,
            bm_length,
            bm_interval,
            repeat=1,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            template=template
        )

        self.searches = searches
        self.inserts = inserts
        self.deletes = deletes

    def run(self):
        """Runs the benchmarks specified for this graph. Overrides PgfPlot.run() method and does NOT call it.."""

        # First, let's run all of the normal mixed-operation benchmarks.
        last_plot = None
        for i in range(len(self.searches)):
            # Store the last plot used, simply so we can use it for plotSizes later.
            last_plot = MixedSIDBenchmarkPlot(
                self.samples,
                self.searches[i],
                self.inserts[i],
                self.deletes[i],
                self.bm_startindex,
                self.bm_length,
                self.bm_interval
            )
            self.addPlot(last_plot)

        # Now, we'll add the plotSizes plot, which requires a little cleverness in MixedSIDBenchmarkPlot
        # to generate its legend key.
        self.functions.append(last_plot.plotSizes)
        self.addPlot(
            last_plot.plotSizes()
        )

    def runAndWrite(self):
        """Overrides PgfPlot.runAndWrite() to call OUR version."""
        self.run()
        self.write()


class MixedSIDBenchmarkPlot(Plot):
    """Performs a sequence of operations of diverse types, reading instructions
    from an input list, and generating benchmarks from them.

    For all functions, the operations list follows the same format. It is a list of pairs, (o, key) where o is
    the operation and key is the data. o must be one of the constants defined in this class. key is the value to be
    passed to the proper function, e.g. (INSERT, 4) might call insert(4)."""

    # Constants for specifying operations.
    # Just in case it rules out some weirdness, let's not use 0.
    SEARCH = 1
    INSERT = 2
    DELETE = 3

    # A little cleverness so we can plot plotSizes with the PgfPlot class.
    legend_text = "Data Structure Size"

    @staticmethod
    def _simOp(op):
        """Returns the change in data structure size as a result of the given operation."""
        if op == MixedSIDBenchmarkPlot.SEARCH:
            return 0
        if op == MixedSIDBenchmarkPlot.INSERT:
            return 1
        if op == MixedSIDBenchmarkPlot.DELETE:
            return -1
        raise ValueError("op must be one of the constants for specifying operations listed in MixedSIDBenchmarkPlot.")

    def __init__(
            self,
            operations,
            search,
            insert,
            delete,
            bm_start,
            bm_length,
            bm_interval
    ):
        """Performs the operations sequence listed, producing the plot points listed."""

        super(MixedSIDBenchmarkPlot, self).__init__()

        self.operations = operations
        self.search = search
        self.insert = insert
        self.delete = delete
        self.bm_start = bm_start
        self.bm_length = bm_length
        self.bm_interval = bm_interval

        # First, let's go up to bm_start.
        for i in range(bm_start):
            op = operations[i]
            self.doOperation(delete, insert, search, op)

        # Now, we'll do the standard benchmark loop....
        # For the remainder of the benchmark cycle, we will use next_benchmark to track when to start a benchmark
        # and p and q to represent the start and end, respectively, of a range that we're calculating.
        p = bm_start
        while p < len(operations):
            # Don't overshoot stop when benchmarking.
            q = min(p + bm_length, len(operations))
            time = Plot.benchmark(
                lambda x: self.doOperation(delete, insert, search, x),
                operations,
                p,
                q
            )
            self.coordinates.append((p, time))
            next_benchmark = p + bm_interval

            # Then, advance to the next benchmark
            p = q
            q = min(next_benchmark, len(operations))
            for i in range(p, q):
                self.doOperation(delete, insert, search, operations[i])

            # Before looping, update p.
            p = q

    def doOperation(self, delete, insert, search, op):
        if op[0] == MixedSIDBenchmarkPlot.SEARCH:
            search(op[1])
        elif op[0] == MixedSIDBenchmarkPlot.INSERT:
            insert(op[1])
        elif op[0] == MixedSIDBenchmarkPlot.DELETE:
            delete(op[1])
        else:
            raise ValueError(
                "op must be one of the constants for specifying operations listed in MixedSIDBenchmarkPlot."
            )

    def plotSizes(self):
        """Generates a plot of the size of a data structure without actually performing the operations themselves.

        Since the operations in bm_length may alter the data structure size significantly, all operations that are
        benchmarked will be simulated, and the median data structure size will be used for each plot point."""

        # Convenience lambda.
        op = lambda x: self.operations[x][0]

        size = 0
        plot = Plot()

        # Do operations until bm_start.
        for i in range(self.bm_start):
            size += MixedSIDBenchmarkPlot._simOp(op(i))

        # Now plot points until we run out of road.
        current_benchmark = self.bm_start
        while current_benchmark < len(self.operations):
            # Very first thing: establish the next benchmark and the end of the current benchmark, since we'll need
            # both of these in various places.
            next_benchmark = min(len(self.operations), current_benchmark + self.bm_interval)
            end_of_benchmark = min(len(self.operations), current_benchmark + self.bm_length)

            # We're at a plot point, so gather all the data structure sizes and plot the median value.

            # We'll do the first by hand, then we can loop through easily.
            bm_sizes = [
                size + MixedSIDBenchmarkPlot._simOp(op(current_benchmark))
            ]

            # Now we'll loop through the rest.
            # Bounds explained:
            # start at current_benchmark + 1 because we just did current_benchmark.
            # End (exclusive of the end) at current_benchmark + bm_length (i.e. the last item being benchmarked),
            # unless that exceeds the operations list, in which case, terminate after the last operation.
            for index in range(current_benchmark + 1, end_of_benchmark):
                bm_sizes.append(
                    bm_sizes[-1] + MixedSIDBenchmarkPlot._simOp(op(index))
                )
                index += 1

            # Now we'll plot the median value
            plot.plotPoint(current_benchmark, statistics.median(bm_sizes))

            # Having finished the benchmark, we'll simulate operations up to the next benchmark, then loop.

            # First, a bit of clean-up.
            size = bm_sizes[-1]

            # Now, we'll simply loop, adjusting sizes.
            for index in range(end_of_benchmark, next_benchmark):
                size += MixedSIDBenchmarkPlot._simOp(op(index))

            # Finally, we're at the next benchmark, so update current_benchmark and loop.
            current_benchmark = next_benchmark

        return plot

