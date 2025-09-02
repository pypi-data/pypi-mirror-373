import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import random
import itertools
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
from plotly.subplots import make_subplots
from typing import Dict, List, Union, Optional

from rich.pretty import pprint
import pandas as pd

# from halib import *
# internal imports
from ..filetype import csvfile
from ..common import ConsoleLog


class DatasetMetrics:
    """Class to store metrics definitions for a specific dataset."""

    def __init__(self, dataset_name: str, metric_names: List[str]):
        self.dataset_name = dataset_name
        self.metric_names = set(metric_names)  # Unique metric names
        self.experiment_results: Dict[str, Dict[str, Union[float, int, None]]] = (
            defaultdict(dict)
        )

    def add_experiment_result(
        self, experiment_name: str, metrics: Dict[str, Union[float, int]]
    ) -> None:
        """Add experiment results for this dataset, only for defined metrics."""
        # normalize metric names to lowercase
        metrics = {k.lower(): v for k, v in metrics.items()}
        # make sure every metric in metrics is defined for this dataset
        for metric in metrics:
            assert metric in self.metric_names, (
                f"Metric <<{metric}>> not defined for dataset <<{self.dataset_name}>>. "
                f"Available metrics: {self.metric_names}"
            )
        for metric in self.metric_names:
            self.experiment_results[experiment_name][metric] = metrics.get(metric)

    def get_metrics(self, experiment_name: str) -> Dict[str, Union[float, int, None]]:
        """Retrieve metrics for a specific experiment."""
        return self.experiment_results.get(
            experiment_name, {metric: None for metric in self.metric_names}
        )

    def __str__(self) -> str:
        return f"Dataset: {self.dataset_name}, Metrics: {', '.join(self.metric_names)}"


class PerfTB:
    """Class to manage performance table data with datasets as primary structure."""

    def __init__(self):
        # Dictionary of dataset_name -> DatasetMetrics
        self.datasets: Dict[str, DatasetMetrics] = {}
        self.experiments: set = set()

    def add_dataset(self, dataset_name: str, metric_names: List[str]) -> None:
        """
        Add a new dataset with its associated metrics.

        Args:
            dataset_name: Name of the dataset
            metric_names: List of metric names for this dataset
        """
        # normalize metric names to lowercase
        metric_names = [metric.lower() for metric in metric_names]
        self.datasets[dataset_name] = DatasetMetrics(dataset_name, metric_names)

    def table_meta(self):
        """
        Return metadata about the performance table.
        """
        return {
            "num_datasets": len(self.datasets),
            "num_experiments": len(self.experiments),
            "datasets_metrics": {
                dataset_name: dataset.metric_names
                for dataset_name, dataset in self.datasets.items()
            }
        }

    def add_experiment(
        self,
        experiment_name: str,
        dataset_name: str,
        metrics: Dict[str, Union[float, int]],
    ) -> None:
        """
        Add experiment results for a specific dataset.

        Args:
            experiment_name: Name or identifier of the experiment
            dataset_name: Name of the dataset
            metrics: Dictionary of metric names and their values
        """
        # normalize metric names to lowercase
        metrics = {k.lower(): v for k, v in metrics.items()}
        if dataset_name not in self.datasets:
            raise ValueError(
                f"Dataset <<{dataset_name}>> not defined. Add dataset first."
            )
        self.experiments.add(experiment_name)
        self.datasets[dataset_name].add_experiment_result(experiment_name, metrics)

    def get_metrics_for_dataset(
        self, experiment_name: str, dataset_name: str
    ) -> Optional[Dict[str, Union[float, int, None]]]:
        """
        Retrieve performance metrics for a specific dataset and experiment.

        Args:
            experiment_name: Name or identifier of the experiment
            dataset_name: Name of the dataset

        Returns:
            Dictionary of metrics or None if dataset not found
        """
        dataset = self.datasets.get(dataset_name)
        if dataset:
            return dataset.get_metrics(experiment_name)
        return None

    def get_all_experiments(self) -> List[str]:
        """Return list of all experiment names."""
        return sorted(self.experiments)

    def get_all_datasets(self) -> List[str]:
        """Return list of all dataset names."""
        return sorted(self.datasets.keys())

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the performance table to a pandas DataFrame with MultiIndex columns.
        Level 1: Datasets
        Level 2: Metrics

        Returns:
            pandas DataFrame with experiments as rows and (dataset, metric) as columns
        """
        # Create MultiIndex for columns (dataset, metric)
        columns = []
        for dataset_name in self.get_all_datasets():
            for metric in sorted(self.datasets[dataset_name].metric_names):
                columns.append((dataset_name, metric))
        columns = pd.MultiIndex.from_tuples(columns, names=["Dataset", "Metric"])

        # Initialize DataFrame with experiments as index
        df = pd.DataFrame(index=sorted(self.experiments), columns=columns)

        # Populate DataFrame
        for exp in self.experiments:
            for dataset_name in self.datasets:
                metrics = self.datasets[dataset_name].get_metrics(exp)
                for metric, value in metrics.items():
                    df.loc[exp, (dataset_name, metric)] = value

        return df

    def plot(
        self,
        save_path: str,
        title: Optional[str] = None,
        custom_highlight_method_fn: Optional[callable] = None,
        custom_sort_exp_fn: Optional[
            callable
        ] = None,  # Function to sort experiments; should accept a list of experiment names and return a sorted list
        open_plot: bool = False,
        show_raw_df: bool = False,
        experiment_names: Optional[List[str]] = None,
        datasets: Optional[List[str]] = None,
        height: int = 400,
        width: int = 700,
    ) -> None:
        """
        Plot comparison of experiments across datasets and their metrics using Plotly.
        Splits plots if metrics have significantly different value ranges.

        Args:
            save_path: Base file path to save the figure(s) (extension optional)
            open_plot: If True, attempts to open the saved image file(s) (Windows only)
            experiment_names: List of experiments to compare (default: all)
            datasets: List of datasets to include (default: all)
            height: Base height of the plot (scaled by # of facet rows)
            width: Width of the plot
            range_diff_threshold: Range threshold to split metrics across different axes
        """
        experiment_names = experiment_names or self.get_all_experiments()
        datasets = datasets or self.get_all_datasets()

        records = []

        for dataset in datasets:
            if dataset not in self.datasets:
                print(f"Warning: Dataset '{dataset}' not found. Skipping...")
                continue

            metric_names = sorted(self.datasets[dataset].metric_names)
            for exp in experiment_names:
                metric_values = self.get_metrics_for_dataset(exp, dataset)
                if not metric_values:
                    continue
                for metric in metric_names:
                    value = metric_values.get(metric)
                    if value is not None:
                        records.append(
                            {
                                "Experiment": exp,
                                "Dataset": dataset,
                                "Metric": metric,
                                "Value": value,
                            }
                        )

        if not records:
            print("No data found to plot.")
            return

        df = pd.DataFrame(records)
        if show_raw_df:
            with ConsoleLog("PerfTB DF"):
                csvfile.fn_display_df(df)

        metric_list = df["Metric"].unique()
        fig = make_subplots(
            rows=len(metric_list),
            cols=1,
            shared_xaxes=False,
            subplot_titles=metric_list,
            vertical_spacing=0.1,
        )

        unique_experiments = df["Experiment"].unique()
        color_cycle = itertools.cycle(px.colors.qualitative.Plotly)

        color_map = {
            exp: color
            for exp, color in zip(unique_experiments, color_cycle)
        }

        pattern_shapes = ["x", "-", "/", "\\", "|", "+", "."]
        pattern_color = "black"  # Color for patterns

        current_our_method = -1  # Start with -1 to avoid index error
        exp_pattern_dict = {}
        shown_legends = set()
        for row_idx, metric in enumerate(metric_list, start=1):
            metric_df = df[df["Metric"] == metric]
            list_exp = list(metric_df["Experiment"].unique())
            if custom_sort_exp_fn:
                list_exp = custom_sort_exp_fn(list_exp)
            for exp in list_exp:
                showlegend = exp not in shown_legends
                shown_legends.add(exp) # since it is a set, it will only keep unique values
                should_highlight = (
                    custom_highlight_method_fn is not None and custom_highlight_method_fn(exp)
                )
                pattern_shape = ""  # default no pattern
                if should_highlight and exp not in exp_pattern_dict:
                    current_our_method += 1
                    pattern_shape = pattern_shapes[
                        current_our_method % len(pattern_shapes)
                    ]
                    exp_pattern_dict[exp] = pattern_shape
                elif exp in exp_pattern_dict:
                    pattern_shape = exp_pattern_dict[exp]
                exp_df = metric_df[metric_df["Experiment"] == exp]
                fig.add_trace(
                    go.Bar(
                        x=exp_df["Dataset"],
                        y=exp_df["Value"],
                        name=f"{exp}",
                        legendgroup=exp,
                        showlegend=showlegend,  # Show legend only for the first row
                        marker=dict(
                            color=color_map[exp],
                            pattern=(
                                dict(shape=pattern_shape, fgcolor=pattern_color)
                                if pattern_shape
                                else None
                            ),
                        ),
                        text=[f"{v:.5f}" for v in exp_df["Value"]],
                        textposition="auto",  # <- position them automatically
                    ),
                    row=row_idx,
                    col=1,
                )

        # Manage layout
        if title is None:
            title = "Experiment Comparison by Metric Groups"
        fig.update_layout(
            height=height * len(metric_list),
            width=width,
            title_text=title,
            barmode="group",
            showlegend=True,
        )

        # Save and open plot
        if save_path:
            export_success = False
            try:
                fig.write_image(save_path, engine="kaleido")
                export_success = True
            # pprint(f"Saved: {os.path.abspath(save_path)}")
            except Exception as e:
                print(f"Error saving plot: {e}")
                pprint(
                    "Failed to save plot. Check this link: https://stackoverflow.com/questions/69016568/unable-to-export-plotly-images-to-png-with-kaleido. Maybe you need to downgrade kaleido version to 0.1.* or install it via pip install kaleido==0.1.*"
                )
                return
            if export_success and open_plot and os.name == "nt":  # Windows
                os.system(f'start "" "{os.path.abspath(save_path)}"')
        return fig

    def to_csv(self, outfile: str, sep=";", condensed_multiindex: bool = True) -> None:
        """
        Save the performance table to a CSV file.

        Args:
            outfile: Path to the output CSV file
        """
        df = self.to_dataframe()
        if condensed_multiindex:
            # Extract levels
            level0 = df.columns.get_level_values(0)
            level1 = df.columns.get_level_values(1)

            # Build new level0 with blanks after first appearance
            new_level0 = []
            prev = None
            for val in level0:
                if val == prev:
                    new_level0.append("")
                else:
                    new_level0.append(val)
                    prev = val

            # Write to CSV
            df.columns = pd.MultiIndex.from_arrays([new_level0, level1])
        df.to_csv(outfile, index=True, sep=sep)

    def display(self) -> None:
        """
        Display the performance table as a DataFrame.
        """
        df = self.to_dataframe()
        csvfile.fn_display_df(df)

    @classmethod
    def _read_condensed_multiindex_csv(cls, filepath: str, sep=";", col_exclude_fn: Optional[callable] = None) -> pd.DataFrame:
        # Read first two header rows
        df = pd.read_csv(filepath, header=[0, 1], sep=sep)
        # Extract levels
        level0 = df.columns.get_level_values(0)
        level1 = df.columns.get_level_values(1)
        # pprint(f'{level0=}')
        # pprint(f'{level1=}')
        # if blank values in level0, fill them after first appearance
        # for level0, we need to fill in blanks after first appearance
        new_level0 = []
        last_non_blank = level0[0]  # Start with the first value
        assert last_non_blank != "", (
            "First level0 value should not be blank. "
            "Check the CSV file format."
        )
        for val in level0:
            if val == "" or "Unnamed: " in val:
                new_level0.append(last_non_blank)
            else:
                new_level0.append(val)
                last_non_blank = val
        # pprint(new_level0)
        # Rebuild MultiIndex
        excluded_indices = []
        if col_exclude_fn:
            excluded_indices = []
            for idx, val in enumerate(new_level0):
                if col_exclude_fn(val):
                    excluded_indices.append(idx)
            for idx, val in enumerate(level1):
                if col_exclude_fn(val):
                    excluded_indices.append(idx)
            excluded_indices = list(set(excluded_indices))

        num_prev_cols = len(new_level0)
        # Remove excluded indices from both levels
        new_level0 = [
            val for idx, val in enumerate(new_level0) if idx not in excluded_indices
        ]
        new_level1 = [
            val for idx, val in enumerate(level1) if idx not in excluded_indices
        ]
        num_after_cols = len(new_level0)
        if num_prev_cols != num_after_cols:
            # get df with only the new level0 index
            df = df.iloc[:, [i for i in range(len(df.columns)) if i not in excluded_indices]]

        df.columns = pd.MultiIndex.from_arrays([new_level0, new_level1])
        return df

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame
    ) -> "PerfTB":
        """
        Load performance table from a DataFrame.

        Args:
            df: Input DataFrame
            method_col_name: Column name for methods
        """
        # console.log('--- PerfTB.from_dataframe ---')
        # csvfile.fn_display_df(df)
        cls_instance = cls()
        # first loop through MultiIndex columns and extract datasets with their metrics
        dataset_metrics = {}
        for (dataset_name, metric_name) in df.columns[1:]:
            if dataset_name not in dataset_metrics:
                dataset_metrics[dataset_name] = []
            dataset_metrics[dataset_name].append(metric_name)
        for dataset_name, metric_names in dataset_metrics.items():
            cls_instance.add_dataset(dataset_name, metric_names)

        def safe_cast(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        for _, row in df.iterrows():
            # Extract experiment name by first column
            experiment_name = row.iloc[0]
            # Iterate over MultiIndex columns (except first column)
            metrics = {}
            for dataset_name in dataset_metrics.keys():
                for metric_name in dataset_metrics[dataset_name]:
                    # Get the value for this dataset and metric
                    value = row[(dataset_name, metric_name)]
                    # Cast to float or None if not applicable
                    metrics[metric_name] = safe_cast(value)

                cls_instance.add_experiment(
                    experiment_name=experiment_name,
                    dataset_name=dataset_name,
                    metrics=metrics,
                )

        return cls_instance

    @classmethod
    def from_csv(
        cls,
        csv_file: str,
        sep: str = ";",
        col_exclude_fn: Optional[callable] = None,
    ) -> "PerfTB":
        """
        Load performance table from a CSV file.

        Args:
            csv_file: Path to the CSV file
            sep: Separator used in the CSV file
        """
        df = cls._read_condensed_multiindex_csv(csv_file, sep=sep, col_exclude_fn=col_exclude_fn)
        return cls.from_dataframe(df)

    def filter_index_info(
        self):
        """
        Filter the index information of the performance table.
        """
        datasets_metrics = {
            dataset_name: dataset.metric_names
            for dataset_name, dataset in self.datasets.items()
        }
        meta_dict = {}
        for i, (dataset_name, metrics) in enumerate(datasets_metrics.items()):
            sorted_metrics = sorted(metrics) # make sure output should be same
            meta_dict[dataset_name] = {
                "index": i,
                "metrics": sorted(
                    list(zip(sorted_metrics, range(len(sorted_metrics))))
                ), # (metric_name, index)
            }
        return meta_dict

    def filter(
        self,
        dataset_list: List[Union[str, int]] = None,  # list of strings or integers
        metrics_list: List[Union[list, str]] = None,
        experiment_list: List[str] = None,
    ) -> "PerfTB":
        """
        Filter the performance table by datasets and experiments.
        Returns a new PerfTB instance with filtered data.
        Args:
            dataset_list: List of dataset names or indices to filter (optional)
            metrics_list: List of metric names to filter (optional). Note that can be pass a list of list (of metric names) to filter by different set of metrics for each dataset. If using a single list, it will be applied to all datasets.
            experiment_list: List of experiment NAMES (string) to filter (optional). Indices are not supported.
        """
        meta_filter_dict = self.filter_index_info()

        if experiment_list is None:
            experiment_list = self.get_all_experiments()
        else:
            # make sure all experiments are found in the performance table
            for exp in experiment_list:
                if exp not in self.experiments:
                    raise ValueError(
                        f"Experiment <<{exp}>> not found in the performance table. Available experiments: {self.get_all_experiments()}"
                    )
        # pprint(f"Filtering experiments: {experiment_list}")
        # get dataset list
        if dataset_list is not None:
            # if all item in dataset_list are integers, convert them to dataset names
            if all(isinstance(item, int) and 0 <= item < len(meta_filter_dict) for item in dataset_list):
                dataset_list = [
                    list(meta_filter_dict.keys())[item] for item in dataset_list
                ]
            elif all(isinstance(item, str) for item in dataset_list):
                # if all items are strings, use them as dataset names
                dataset_list = [
                    item for item in dataset_list if item in meta_filter_dict
                ]
            else:
                raise ValueError(
                    f"dataset_list should be a list of strings (dataset names) or integers (indices, should be <= {len(meta_filter_dict) - 1}). Got: {dataset_list}"
                )
        else:
            dataset_list = self.get_all_datasets()

        filter_metrics_ls = [] # [list_metric_db_A, list_metric_db_B, ...]
        all_ds_metrics = []
        for dataset_name in dataset_list:
            ds_meta = meta_filter_dict.get(dataset_name, None)
            if ds_meta:
                ds_metrics = ds_meta["metrics"]
                all_ds_metrics.append([metric[0] for metric in ds_metrics])

        if metrics_list is None:
            filter_metrics_ls = all_ds_metrics
        elif isinstance(metrics_list, list):
            all_string = all(isinstance(item, str) for item in metrics_list)
            if all_string:
                # normalize metrics_list to lowercase
                metrics_list = [metric.lower() for metric in metrics_list]
                filter_metrics_ls = [metrics_list] * len(dataset_list)
            else:
                all_list = all(isinstance(item, list) for item in metrics_list)
                pprint(f'{all_list=}')
                if all_list:
                    print('b')
                    if len(metrics_list) != len(dataset_list):
                        raise ValueError(
                            f"metrics_list should be a list of strings (metric names) or a list of lists of metric names for each dataset. Got: {len(metrics_list)} metrics for {len(dataset_list)} datasets."
                        )
                    # normalize each list of metrics to lowercase
                    filter_metrics_ls = [
                        [metric.lower() for metric in item] for item in metrics_list
                    ]

        else:
            raise ValueError(
                f"metrics_list should be a list of strings (metric names) or a list of lists of metric names for each dataset. Got: {metrics_list}"
            )

        # make sure that all metrics in filtered_metrics_list are valid for the datasets
        final_metrics_list = []
        for idx, dataset_name in enumerate(dataset_list):
            valid_metrics_list = all_ds_metrics[idx]
            current_metrics = filter_metrics_ls[idx]
            new_valid_ds_metrics = []
            for metric in current_metrics:
                if metric in valid_metrics_list:
                    new_valid_ds_metrics.append(metric)
            assert len(new_valid_ds_metrics) > 0, (
                f"No valid metrics found for dataset <<{dataset_name}>>. "
                f"Available metrics: {valid_metrics_list}. "
                f"Filtered metrics: {current_metrics}"
            )
            final_metrics_list.append(new_valid_ds_metrics)

        assert len(experiment_list) > 0, "No experiments to filter."
        assert len(dataset_list) > 0, "No datasets to filter."
        assert len(final_metrics_list) > 0, "No metrics to filter."
        filtered_tb = PerfTB()
        for db, metrics in zip(dataset_list, final_metrics_list):
            # add dataset with its metrics
            filtered_tb.add_dataset(db, metrics)

        # now add experiments with their metrics
        for exp in experiment_list:
            for db, metrics in zip(dataset_list, final_metrics_list):
                # get metrics for this experiment and dataset
                metrics_dict = self.get_metrics_for_dataset(exp, db)
                if metrics_dict:
                    # filter metrics to only those defined for this dataset
                    filtered_metrics = {k: v for k, v in metrics_dict.items() if k in metrics}
                    if filtered_metrics:
                        filtered_tb.add_experiment(exp, db, filtered_metrics)

        return filtered_tb


def test_perftb_create() -> PerfTB:
    # Create a performance table
    perf_table = PerfTB()

    # Define datasets and their metrics first
    perf_table.add_dataset("dataset1", ["accuracy", "f1_score"])
    perf_table.add_dataset("dataset2", ["accuracy", "f1_score", "precision"])

    # Add experiment results
    perf_table.add_experiment(
        experiment_name="our_method1",
        dataset_name="dataset1",
        metrics={"accuracy": 100, "f1_score": 0.93},
    )
    perf_table.add_experiment(
        experiment_name="our_method2",
        dataset_name="dataset2",
        metrics={"accuracy": 100, "precision": 0.87},  # Missing precision will be None
    )
    perf_table.add_experiment(
        experiment_name="our_method2",
        dataset_name="dataset1",
        metrics={"accuracy": 90, "f1_score": 0.85},
    )
    method_list = [f"method{idx}" for idx in range(3, 7)]
    # add random values for methods 3-6
    for method in method_list:
        perf_table.add_experiment(
            experiment_name=method,
            dataset_name="dataset1",
            metrics={
                "accuracy": random.randint(80, 100),
                "f1_score": random.uniform(0.7, 0.95),
            },
        )
        perf_table.add_experiment(
            experiment_name=method,
            dataset_name="dataset2",
            metrics={
                "accuracy": random.randint(80, 100),
                "precision": random.uniform(0.7, 0.95),
                "f1_score": random.uniform(0.7, 0.95),
            },
        )

    # Get metrics for a specific dataset
    metrics = perf_table.get_metrics_for_dataset("model1", "f1_score")
    if metrics:
        print(f"\nMetrics for model1 on dataset1: {metrics}")

    return perf_table

def test_perftb_dataframe() -> None:
    # Create a performance table
    perf_table = test_perftb_create()

    # Convert to DataFrame
    df = perf_table.to_dataframe()
    print("\nPerformance Table as DataFrame:")
    csvfile.fn_display_df(df)

    # Save to CSV
    perf_table.to_csv("zout/perf_tb.csv", sep=";")

def test_perftb_plot() -> None:
    # Create a performance table
    perf_table = test_perftb_create()

    # Plot the performance table
    perf_table.plot(
        save_path="zout/perf_tb.svg",
        title="Performance Comparison",
        custom_highlight_method_fn=lambda exp: exp.startswith("our_method"),
        custom_sort_exp_fn=lambda exps: sorted(exps, reverse=True),
        open_plot=False,
        show_raw_df=False,
    )

def test_load_perftb() -> None:
    # Load performance table from CSV
    def col_exclude_fn(col_name: str) -> bool:
        # Exclude columns that are not metrics (e.g., "Unnamed" columns)
        return col_name in ["Year", "data split", "test procedure", "code?"]

    perf_table = PerfTB.from_csv("test/bench.csv", sep=";", col_exclude_fn=col_exclude_fn)
    # print("\nLoaded Performance Table:")
    # perf_table.display()
    perf_table.to_csv("zout/loaded_perf_tb.csv", sep=";")

    # Plot loaded performance table
    perf_table.plot(
        save_path="zout/loaded_perf_plot.svg",
        title="Loaded Performance Comparison",
        custom_highlight_method_fn=lambda exp: exp.startswith("Ours"),
        custom_sort_exp_fn=lambda exps: sorted(exps, reverse=True),
        open_plot=False,
        show_raw_df=False,
    )
    return perf_table

def test_filtered_perftb() -> None:
    perf_table_item = test_load_perftb()
    # pprint(perf_table_item.meta())
    pprint(perf_table_item.filter_index_info())
    perf_table_item.filter(
        dataset_list=[0, 2],  # Use indices of datasets
        # dataset_list=[
        #     "BOWFire_dataset_chino2015bowfire (small)",
        #     "FD-Dataset_li2020efficient (large)",
        # ],
        metrics_list=[
            "acc",
            "f1",
        ],  # [["acc"], ["f1"]],  # Use a single list of metrics for all datasets or a list of lists for different metrics per dataset
        # experiment_list=["ADFireNet_yar2023effective"],
    ).plot(
        save_path="zout/filtered_perf_tb.svg",
        chk_highlight_method_fn=lambda exp: exp.startswith("Ours"),
        custom_sort_exp_fn=lambda exps: sorted(exps, reverse=True),
        title="Filtered Performance Comparison",
    )

def test_mics() -> None:
    # Test reading a CSV with MultiIndex columns
    perf_table = test_perftb_create()
    perf_table.display()
    perf_table.plot(
        save_path="zout/test1.svg",
        title="Performance Comparison",
        custom_highlight_method_fn=lambda exp: exp.startswith("our_"),
        custom_sort_exp_fn=lambda exps: sorted(exps, reverse=True),
        open_plot=False,
    )
    perf_table.to_csv("zout/perf_tb1.csv", sep=";")
    tb = PerfTB.from_csv("./zout/perf_tb1.csv", sep=";")
    tb.display()
    ftb = tb.filter(
        dataset_list=[1],
        metrics_list=["precision"],
        experiment_list=["method3", "method6"],
    )
    ftb.display()

    ftb.plot(
        save_path="zout/perf_tb11_plot.svg",
        title="Performance Comparison",
        custom_highlight_method_fn=lambda exp: exp.startswith("our_"),
        custom_sort_exp_fn=lambda exps: sorted(exps, reverse=True),
        open_plot=True,
    )
def test_bench2():
    perftb = PerfTB.from_csv(
        "test/bench2.csv",
        sep=";")
    perftb.display()
    perftb.plot(
        save_path="zout/bench2_plot.svg",
        title="Bench2 Performance Comparison",
        open_plot=True,
    )


# Example usage
if __name__ == "__main__":
    # test_mics()
    test_bench2()
