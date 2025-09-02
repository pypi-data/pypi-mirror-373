import os
import time
import json

from pathlib import Path
from pprint import pprint
from threading import Lock

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px  # for dynamic color scales
from ..common import ConsoleLog

from loguru import logger

class zProfiler:
    """A singleton profiler to measure execution time of contexts and steps.

    Args:
        interval_report (int): Frequency of periodic reports (0 to disable).
        stop_to_view (bool): Pause execution to view reports if True (only in debug mode).
        output_file (str): Path to save the profiling report.
        report_format (str): Output format for reports ("json" or "csv").

    Example:
        prof = zProfiler()
        prof.ctx_start("my_context")
        prof.step_start("my_context", "step1")
        time.sleep(0.1)
        prof.step_end("my_context", "step1")
        prof.ctx_end("my_context")
    """

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(
        self,
    ):
        if not hasattr(self, "_initialized"):
            self.time_dict = {}
            self._initialized = True

    def ctx_start(self, ctx_name="ctx_default"):
        if not isinstance(ctx_name, str) or not ctx_name:
            raise ValueError("ctx_name must be a non-empty string")
        if ctx_name not in self.time_dict:
            self.time_dict[ctx_name] = {
                "start": time.perf_counter(),
                "step_dict": {},
                "report_count": 0,
            }
        self.time_dict[ctx_name]["report_count"] += 1

    def ctx_end(self, ctx_name="ctx_default", report_func=None):
        if ctx_name not in self.time_dict:
            return
        self.time_dict[ctx_name]["end"] = time.perf_counter()
        self.time_dict[ctx_name]["duration"] = (
            self.time_dict[ctx_name]["end"] - self.time_dict[ctx_name]["start"]
        )

    def step_start(self, ctx_name, step_name):
        if not isinstance(step_name, str) or not step_name:
            raise ValueError("step_name must be a non-empty string")
        if ctx_name not in self.time_dict:
            return
        if step_name not in self.time_dict[ctx_name]["step_dict"]:
            self.time_dict[ctx_name]["step_dict"][step_name] = []
        self.time_dict[ctx_name]["step_dict"][step_name].append([time.perf_counter()])

    def step_end(self, ctx_name, step_name):
        if (
            ctx_name not in self.time_dict
            or step_name not in self.time_dict[ctx_name]["step_dict"]
        ):
            return
        self.time_dict[ctx_name]["step_dict"][step_name][-1].append(time.perf_counter())

    def _step_dict_to_detail(self, ctx_step_dict):
        """
                'ctx_step_dict': {
        │   │   'preprocess': [
        │   │   │   [278090.947465806, 278090.960484853],
        │   │   │   [278091.178424035, 278091.230944486],
        │   │   'infer': [
        │   │   │   [278090.960490534, 278091.178424035],
        │   │   │   [278091.230944486, 278091.251378469],
        │   }
        """
        assert (
            len(ctx_step_dict.keys()) > 0
        ), "step_dict must have only one key (step_name) for detail."

        for step_name, time_list in ctx_step_dict.items():
            normed_ctx_step_dict = {}
            if not isinstance(ctx_step_dict[step_name], list):
                raise ValueError(f"Step data for {step_name} must be a list")
            step_name = list(ctx_step_dict.keys())[0]
            normed_time_ls = []
            for idx, time_data in enumerate(time_list):
                elapsed_time = -1
                if len(time_data) == 2:
                    start, end = time_data[0], time_data[1]
                    elapsed_time = end - start
                normed_time_ls.append((idx, elapsed_time))  # including step
            normed_ctx_step_dict[step_name] = normed_time_ls
            return normed_ctx_step_dict

    def get_report_dict(self, with_detail=False):
        report_dict = {}
        for ctx_name, ctx_dict in self.time_dict.items():
            report_dict[ctx_name] = {
                "duration": ctx_dict.get("duration", 0.0),
                "step_dict": {
                    "summary": {"avg_time": {}, "percent_time": {}},
                    "detail": {},
                },
            }

            if with_detail:
                report_dict[ctx_name]["step_dict"]["detail"] = (
                    self._step_dict_to_detail(ctx_dict["step_dict"])
                )
            avg_time_list = []
            epsilon = 1e-5
            for step_name, step_list in ctx_dict["step_dict"].items():
                durations = []
                try:
                    for time_data in step_list:
                        if len(time_data) != 2:
                            continue
                        start, end = time_data
                        durations.append(end - start)
                except Exception as e:
                    logger.error(
                        f"Error processing step {step_name} in context {ctx_name}: {e}"
                    )
                    continue
                if not durations:
                    continue
                avg_time = sum(durations) / len(durations)
                if avg_time < epsilon:
                    continue
                avg_time_list.append((step_name, avg_time))
            total_avg_time = (
                sum(time for _, time in avg_time_list) or 1e-10
            )  # Avoid division by zero
            for step_name, avg_time in avg_time_list:
                report_dict[ctx_name]["step_dict"]["summary"]["percent_time"][
                    f"per_{step_name}"
                ] = (avg_time / total_avg_time) * 100.0
                report_dict[ctx_name]["step_dict"]["summary"]["avg_time"][
                    f"avg_{step_name}"
                ] = avg_time
            report_dict[ctx_name]["step_dict"]["summary"][
                "total_avg_time"
            ] = total_avg_time
            report_dict[ctx_name]["step_dict"]["summary"] = dict(
                sorted(report_dict[ctx_name]["step_dict"]["summary"].items())
            )
        return report_dict

    @classmethod
    @classmethod
    def plot_formatted_data(
        cls, profiler_data, outdir=None, file_format="png", do_show=False, tag=""
    ):
        """
        Plot each context in a separate figure with bar + pie charts.
        Save each figure in the specified format (png or svg).
        """

        if outdir is not None:
            os.makedirs(outdir, exist_ok=True)

        if file_format.lower() not in ["png", "svg"]:
            raise ValueError("file_format must be 'png' or 'svg'")

        results = {}  # {context: fig}

        for ctx, ctx_data in profiler_data.items():
            summary = ctx_data["step_dict"]["summary"]
            avg_times = summary["avg_time"]
            percent_times = summary["percent_time"]

            step_names = [s.replace("avg_", "") for s in avg_times.keys()]
            # pprint(f'{step_names=}')
            n_steps = len(step_names)

            assert n_steps > 0, "No steps found for context: {}".format(ctx)
            # Generate dynamic colors
            colors = px.colors.sample_colorscale(
                "Viridis", [i / (n_steps - 1) for i in range(n_steps)]
            ) if n_steps > 1 else [px.colors.sample_colorscale("Viridis", [0])[0]]
            # pprint(f'{len(colors)} colors generated for {n_steps} steps')
            color_map = dict(zip(step_names, colors))

            # Create figure
            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=[f"Avg Time", f"% Time"],
                specs=[[{"type": "bar"}, {"type": "pie"}]],
            )

            # Bar chart
            fig.add_trace(
                go.Bar(
                    x=step_names,
                    y=list(avg_times.values()),
                    text=[f"{v*1000:.2f} ms" for v in avg_times.values()],
                    textposition="outside",
                    marker=dict(color=[color_map[s] for s in step_names]),
                    name="",  # unified legend
                    showlegend=False,
                ),
                row=1,
                col=1,
            )

            # Pie chart (colors match bar)
            fig.add_trace(
                go.Pie(
                    labels=step_names,
                    values=list(percent_times.values()),
                    marker=dict(colors=[color_map[s] for s in step_names]),
                    hole=0.4,
                    name="",
                    showlegend=True,
                ),
                row=1,
                col=2,
            )
            tag_str = tag if tag and len(tag) > 0 else ""
            # Layout
            fig.update_layout(
                title_text=f"[{tag_str}] Context Profiler: {ctx}",
                width=1000,
                height=400,
                showlegend=True,
                legend=dict(title="Steps", x=1.05, y=0.5, traceorder="normal"),
                hovermode="x unified",
            )

            fig.update_xaxes(title_text="Steps", row=1, col=1)
            fig.update_yaxes(title_text="Avg Time (ms)", row=1, col=1)

            # Show figure
            if do_show:
                fig.show()

            # Save figure
            if outdir is not None:
                file_prefix = ctx if len(tag_str) == 0 else f"{tag_str}_{ctx}"
                file_path = os.path.join(outdir, f"{file_prefix}_summary.{file_format.lower()}")
                fig.write_image(file_path)
                print(f"Saved figure: {file_path}")

            results[ctx] = fig

        return results

    def report_and_plot(self, outdir=None, file_format="png", do_show=False, tag=""):
        """
        Generate the profiling report and plot the formatted data.

        Args:
            outdir (str): Directory to save figures. If None, figures are only shown.
            file_format (str): Target file format, "png" or "svg". Default is "png".
            do_show (bool): Whether to display the plots. Default is False.
        """
        report = self.get_report_dict()
        self.get_report_dict(with_detail=False)
        return self.plot_formatted_data(
            report, outdir=outdir, file_format=file_format, do_show=do_show, tag=tag
        )
    def meta_info(self):
        """
        Print the structure of the profiler's time dictionary.
        Useful for debugging and understanding the profiler's internal state.
        """
        for ctx_name, ctx_dict in self.time_dict.items():
            with ConsoleLog(f"Context: {ctx_name}"):
                step_names = list(ctx_dict['step_dict'].keys())
                for step_name in step_names:
                    pprint(f"Step: {step_name}")

    def save_report_dict(self, output_file, with_detail=False):
        try:
            report = self.get_report_dict(with_detail=with_detail)
            with open(output_file, "w") as f:
                json.dump(report, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save report to {output_file}: {e}")
