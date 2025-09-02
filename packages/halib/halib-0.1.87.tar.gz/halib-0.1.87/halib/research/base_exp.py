from abc import ABC, abstractmethod

from ..research.base_config import ExpBaseConfig
from ..research.perfcalc import PerfCalc
from ..research.metrics import MetricsBackend

# ! SEE https://github.com/hahv/base_exp for sample usage
class BaseExperiment(PerfCalc, ABC):
    """
    Base class for experiments.
    Orchestrates the experiment pipeline using a pluggable metrics backend.
    """

    def __init__(self, config: ExpBaseConfig):
        self.config = config
        self.metric_backend = None

    # -----------------------
    # PerfCalc Required Methods
    # -----------------------
    def get_dataset_name(self):
        return self.config.get_dataset_cfg().get_name()

    def get_experiment_name(self):
        return self.config.get_cfg_name()

    def get_metric_backend(self):
        if not self.metric_backend:
            self.metric_backend = self.prepare_metrics(self.config.get_metric_cfg())
        return self.metric_backend

    # -----------------------
    # Abstract Experiment Steps
    # -----------------------
    @abstractmethod
    def init_general(self, general_cfg):
        """Setup general settings like SEED, logging, env variables."""
        pass

    @abstractmethod
    def prepare_dataset(self, dataset_cfg):
        """Load/prepare dataset."""
        pass

    @abstractmethod
    def prepare_metrics(self, metric_cfg) -> MetricsBackend:
        """
        Prepare the metrics for the experiment.
        This method should be implemented in subclasses.
        """
        pass

    @abstractmethod
    def exec_exp(self, *args, **kwargs):
        """Run experiment process, e.g.: training/evaluation loop.
        Return: raw_metrics_data, and extra_data as input for calc_and_save_exp_perfs
        """
        pass

    def eval_exp(self):
        """Optional: re-run evaluation from saved results."""
        pass

    # -----------------------
    # Main Experiment Runner
    # -----------------------
    def run_exp(self, do_calc_metrics=True, *args, **kwargs):
        """
        Run the whole experiment pipeline.
        Params:
            + 'outfile' to save csv file results,
            + 'outdir' to set output directory for experiment results.
            + 'return_df' to return a DataFrame of results instead of a dictionary.

        Full pipeline:
            1. Init
            2. Dataset
            3. Metrics Preparation
            4. Save Config
            5. Execute
            6. Calculate & Save Metrics
        """
        self.init_general(self.config.get_general_cfg())
        self.prepare_dataset(self.config.get_dataset_cfg())
        self.prepare_metrics(self.config.get_metric_cfg())

        # Save config before running
        self.config.save_to_outdir()

        # Execute experiment
        results = self.exec_exp(*args, **kwargs)
        if do_calc_metrics:
            metrics_data, extra_data = results
            # Calculate & Save metrics
            perf_results = self.calc_and_save_exp_perfs(
                raw_metrics_data=metrics_data, extra_data=extra_data, *args, **kwargs
            )
            return perf_results
        else:
            return results
