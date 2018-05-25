import trender


class PgfPlot:
    """Represents a LaTeX pgfplots graph generated from benchmarking algorithms.

    The typical workflow might look something like this:
    1. Initialize the PgfPlot
    2. Add Plots
    3. Generate"""

    def __init__(
            self,
            functions,
            samples,
            startindex,
            stopindex,
            bm_startindex,
            bm_length,
            bm_interval,
            filename,
            xlabel="",
            ylabel="",
            title="",
            caption="",
            template="figure.template.tex",
    ):
        """Initializes all options of a BenchmarkGraph.

        Benchmarking:
        Starting with samples[startindex], the benchmark will call function(x), passing subsequent items from samples
        as x. When the index reaches bm_start, it will time the function(x) calls for bm_length indices, divide the
        resulting time by bm_length, and record that time as a single data point on the Plot. Then, it will proceed
        until it reaches index bm_start + bm_interval, where it will create another data point for the plot. It will
        proceed in this way until it reaches stopindex. stopindex will not be included in the benchmark.

        functions: list of functions to benchmark. Each function will become a plot.
        samples: list of input data for the functions. This list will be processed in order.
        startindex: the first index in samples to insert during benchmarking.
        stopindex: the stop index for benchmarking; when this index is reached, the benchmark ends.
        bm_startindex: the first index in the first plot point's range. The timer starts when this index is reached.
        bm_length: the length of each timed sample range in the benchmark, specified in indices.
        bm_interval: the number of indices between timed sample range start points, e.g. 10 to start at 10, 20, 30, etc.
        filename: the name of the file (with optional path) to which the output should be written, e.g. "plots/test.tex"
        xlabel: the x-axis label, e.g. \begin{axis}[xlabel={foo}]
        ylabel: the y-axis label, e.g. \begin{axis}[xlabel={foo}]
        title: the graph title, e.g. \begin{axis}[title={foo}]
        caption: the figure caption, e.g. \caption{foo}
        template: the name of the template file to use."""

        self.functions = functions          # For benchmarking.
        self.samples = samples              # For benchmarking.
        self.startindex = startindex        # For benchmarking.
        self.stopindex = stopindex          # For benchmarking.
        self.bm_startindex = bm_startindex  # For benchmarking.
        self.bm_length = bm_length          # For benchmarking.
        self.bm_interval = bm_interval      # For benchmarking.
        self.xlabel = xlabel                # LaTeX fields.
        self.ylabel = ylabel                # LaTeX fields.
        self.title = title                  # LaTeX fields.
        self.caption = caption              # LaTeX fields.
        self.plots = [] * len(functions)    # Will hold created Plot objects created for corresponding functions.

        with open(template, 'r') as f:
            self.template = trender.TRender(f.read())

    def run(self):
        """Runs becnhmarks and writes the LaTeX Figure object with the results."""

        # First, run all the benchmarks, creating a plot for each.
        for f in range(len(self.functions)):
            self.plots[f] = # TODO Call refactored plot generation method!

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