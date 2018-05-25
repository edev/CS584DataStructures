import trender
import statistics
from plot import BenchmarkPlot


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
            caption="",
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
        self.caption = caption                  # LaTeX fields.
        self.plots = [] * len(functions)        # Will hold created Plot objects created for corresponding functions.

        with open(template, 'r') as f:
            self.template = trender.TRender(f.read())

    def run(self):
        """Runs benchmarks and writes the LaTeX Figure object with the results."""

        # First, run all the benchmarks, creating a plot for each.
        for f in range(len(self.functions)):
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

        # Then, prepare the plots for LaTeX output.
        plots = ""
        for plot in self.plots:
            plots += plot.get_latex()
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
        with open(self.filename, "w") as f:
            f.write(output)