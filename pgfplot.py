import trender
import statistics
from plot import Plot, BenchmarkPlot


class PgfPlot:
    """Represents a LaTeX pgfplots graph generated from benchmarking algorithms.

    The typical workflow might look something like this:
    1. Initialize the PgfPlot
    2. Add Plots
    3. Generate"""

    def __init__(
            self,
            filename,
            functions,
            samples,
            startindex,
            stopindex,
            bm_startindex,
            bm_length,
            bm_interval,
            repeat,
            combine_method=statistics.median,
            xlabel="",
            ylabel="",
            title="",
            template="figure.template.tex",
    ):
        """Initializes all options of a BenchmarkGraph, which fall into two categories, benchmarking and LaTeX output.

        Benchmarking:
        See Plot.benchmark method.

        Benchmarking options:
        functions: list of functions to benchmark. Each function will become a plot.
        samples: list of input data for the functions. This list will be processed in order.
        startindex: the first index in samples to insert during benchmarking.
        stopindex: the stop index for benchmarking; when this index is reached, the benchmark ends.
        bm_startindex: the first index in the first plot point's range. The timer starts when this index is reached.
        bm_length: the length of each timed sample range in the benchmark, specified in indices.
        bm_interval: the number of indices between timed sample range start points, e.g. 10 to start at 10, 20, 30, etc.
        repeat: the number of times to repeat the test on samples.

        LaTeX:
        Outputs a LaTeX file containg a single figure object that draws a graph of the specified benchmark.

        LaTeX output options:
        filename: the name of the file (with optional path) to which the output should be written, e.g. "plots/test.tex"
        xlabel: the x-axis label, e.g. \begin{axis}[xlabel={foo}]
        ylabel: the y-axis label, e.g. \begin{axis}[xlabel={foo}]
        title: the graph title, e.g. \begin{axis}[title={foo}]
        caption: the figure caption, e.g. \caption{foo}
        template: the name of the template file to use."""

        self.filename = filename                # For LaTeX output.
        self.functions = functions              # For benchmarking.
        self.samples = samples                  # For benchmarking.
        self.startindex = startindex            # For benchmarking.
        self.stopindex = stopindex              # For benchmarking.
        self.bm_startindex = bm_startindex      # For benchmarking.
        self.bm_length = bm_length              # For benchmarking.
        self.bm_interval = bm_interval          # For benchmarking.
        self.repeat = repeat                    # For benchmarking.
        self.combine_method = combine_method    # For benchmarking.
        self.xlabel = xlabel                    # LaTeX fields.
        self.ylabel = ylabel                    # LaTeX fields.
        self.title = title                      # LaTeX fields.
        self.plots = []                         # Will hold created Plot objects created for corresponding functions.

        with open(template, 'r') as f:
            self.template = trender.TRender(f.read())

    def addPlot(self, p: Plot):
        """Adds the Plot p to the PgfPlot. This plot is treated as final data and will not be modified during run()."""

        self.plots.append(p)


    def write(self):
        plots = ""
        for plot in self.plots:
            plots += plot.get_latex()
        # Then, strip off the final "\n".
        plots = plots[0:-1]

        # Now, prepare the caption.
        self.caption = \
            "Average of {} operations, benchmarked every {}, starting at {}."
        self.caption = self.caption.format(
            self.bm_length,
            self.bm_interval,
            self.bm_startindex
        )
        if self.repeat > 1:
            self.caption += " Median of {} runs.".format(self.repeat)

        # Prepare the legend.
        legend_items = [0] * len(self.functions)
        for i in range(len(self.functions)):
            legend_items[i] = self.functions[i].__self__.__class__.legend_text
        legend_inner_text = ", ".join(legend_items)
        legend = "\legend{" + legend_inner_text + "}"

        # Next, render the template.
        output = self.template.render({
            "xlabel": self.xlabel,
            "ylabel": self.ylabel,
            "title": self.title,
            "caption": self.caption,
            "plots": plots,
            "legend": legend
        })

        # Finally, write the file.
        with open(self.filename, "w") as f:
            f.write(output)


    def run(self):
        """Runs benchmarks for all functions in self.functions, producing plots for them."""

        print("Running benchmarks for: " + self.title)
        for f in range(len(self.functions)):
            print("\tRunning benchmark {}...".format(f + 1))
            self.plots.append(
                BenchmarkPlot(
                    self.functions[f],
                    self.samples,
                    self.startindex,
                    self.stopindex,
                    self.bm_startindex,
                    self.bm_length,
                    self.bm_interval,
                    self.repeat,
                    self.combine_method
                )
            )


    def runAndWrite(self):
        """Runs benchmarks and writes the LaTeX Figure object with the results."""

        # First, run all the benchmarks, creating a plot for each.
        self.run()

        # Then, prepare the plots for LaTeX output.
        self.write()