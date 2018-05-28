from pgfplot import PgfPlot
from plot import Plot

class SIDGraphSet:
    """Coordinates 3 PgfPlots and an arbitrary number of SIDBenchmarks as one, unified graph set.

    An SIDBenchmark generates 3 Plots for the same data structure, pertaining to search, insert, and delete (SID).
    A PgfPlot, meanwhile, combines multiple plots pertaining to one subject and outputs one graph.
    This class coordinates multiple SIDBenchmarks across 3 PgfPlots, outputting 3 graphs: search, insert, and delete.

    Since all 3 graphs are coordinated, this class is designed around sharing the sample sets across SIDBenchmarks."""

    def __init__(
            self,
            search_filename,
            insert_filename,
            delete_filename,
            searches,
            inserts,
            deletes,
            search_samples,
            insert_samples,
            delete_samples,
            stop,
            bm_start,
            bm_length,
            bm_interval,
            xlabel="",
            ylabel="",
            title="",
            template="figure.template.tex"
    ):
        """Runs all SIDBenchmarks and produces the graphs immediately and synchronously.

        The searches, inserts, and deletes lists should be in the same order, so that searches[i], inserts[i], and
        deletes[i] all pertain to the same data structure.

        search_filename: the filename, with optional path, to which the search graph will be written.
        insert_filename: the filename, with optional path, to which the insert graph will be written.
        delete_filename: the filename, with optional path, to which the delete graph will be written.
        searches: list of search functions.
        inserts: list of insert functions.
        deletes: list of delete functions.
        search_samples: a list of sample inputs to search, which will be used for all SIDBenchmarks.
        insert_samples: a list of sample inputs to insert, which will be used for all SIDBenchmarks.
        delete_samples: a list of sample inputs to delete, which will be used for all SIDBenchmarks.
        stop: see SIDBenchmark.
        bm_start: see SIDBenchmark.
        bm_interval: see SIDBenchmark.

        The repeat and combine_method fields of PgfPlot are not used here, because SIDBenchmark does not support
        the repeat option."""

        # Setup PgfPlots objects. Note: we will bypass its auto-run functionality by not providing either samples
        # or functions to run. In fact, all options related to benchmarking will be empty.
        search_graph = PgfPlot(
            filename=search_filename,
            functions=[],
            samples=[],
            startindex=0,
            stopindex=0,
            bm_startindex=0,
            bm_length=0,
            bm_interval=0,
            repeat=0,
            combine_method=None,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            template=template
        )
        insert_graph = PgfPlot(
            filename=insert_filename,
            functions=[],
            samples=[],
            startindex=0,
            stopindex=0,
            bm_startindex=0,
            bm_length=0,
            bm_interval=0,
            repeat=0,
            combine_method=None,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            template=template
        )
        delete_graph = PgfPlot(
            filename=delete_filename,
            functions=[],
            samples=[],
            startindex=0,
            stopindex=0,
            bm_startindex=0,
            bm_length=0,
            bm_interval=0,
            repeat=0,
            combine_method=None,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            template=template
        )

        # Now, we'll run all of our data collection. We'll just use len(searches) as our bound, because
        # if searches, inserts, and deletes aren't all the same size, we're probably in trouble anyway
        # and the user needs to know (i.e. crash).
        benchmarks = []
        for i in range(len(searches)):
            benchmarks.append(
                SIDBenchmark(
                    searches[i],
                    inserts[i],
                    deletes[i],
                    search_samples,
                    insert_samples,
                    delete_samples,
                    stop,
                    bm_start,
                    bm_length,
                    bm_interval
                )
            )

        # Next, we'll add our plots to the PgfPlots objects.
        for i in range(len(benchmarks)):
            search_graph.addPlot(benchmarks[i].search_plot)
            insert_graph.addPlot(benchmarks[i].insert_plot)
            delete_graph.addPlot(benchmarks[i].delete_plot)

        # Finally, we'll run our PgfPlots.
        search_graph.run()
        insert_graph.run()
        delete_graph.run()


class SIDBenchmark:
    """Performs similar functions to BenchmarkPlot, except that it specifically calls a sequence of search, insert,
    and delete operations and produces 3 Plots corresponding to these operations."""

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