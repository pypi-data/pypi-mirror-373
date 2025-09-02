# -------------------------------
# Metrics Backend Interface
# -------------------------------
import inspect
from typing import Dict, Union, List, Any
from abc import ABC, abstractmethod

class MetricsBackend(ABC):
    """Interface for pluggable metrics computation backends."""

    def __init__(self, metrics_info: Union[List[str], Dict[str, Any]]):
        """
        Initialize the backend with optional metrics_info.
        """
        self.metric_info = metrics_info
        self.validate_metrics_info(self.metric_info)

    @property
    def metric_names(self) -> List[str]:
        """
        Return a list of metric names.
        If metric_info is a dict, return its keys; if it's a list, return it directly.
        """
        if isinstance(self.metric_info, dict):
            return list(self.metric_info.keys())
        elif isinstance(self.metric_info, list):
            return self.metric_info
        else:
            raise TypeError("metric_info must be a list or a dict")

    def validate_metrics_info(self, metrics_info):
        if isinstance(metrics_info, list):
            return metrics_info
        elif isinstance(metrics_info, dict):
            return {k: v for k, v in metrics_info.items() if isinstance(k, str)}
        else:
            raise TypeError(
                "metrics_info must be a list of strings or a dict with string keys"
            )

    @abstractmethod
    def compute_metrics(
        self, metrics_info: Union[List[str], Dict[str, Any]],  metrics_data_dict: Dict[str, Any], *args, **kwargs
    ) -> Dict[str, Any]:
        pass

    def prepare_metrics_backend_data(
        self, raw_metric_data, *args, **kwargs
    ):
        """
        Prepare the data for the metrics backend.
        This method can be overridden by subclasses to customize data preparation.
        """
        return raw_metric_data

    def calc_metrics(
        self,  metrics_data_dict: Dict[str, Any], *args, **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate metrics based on the provided metrics_info and data.
        This method should be overridden by subclasses to implement specific metric calculations.
        """
        # prevalidate the metrics_data_dict
        for metric in self.metric_names:
            if metric not in metrics_data_dict:
                raise ValueError(f"Metric '{metric}' not found in provided data.")
        # Prepare the data for the backend
        metrics_data_dict = self.prepare_metrics_backend_data(
            metrics_data_dict, *args, **kwargs
        )
        # Call the abstract method to compute metrics
        return self.compute_metrics(self.metric_info, metrics_data_dict, *args, **kwargs)

class TorchMetricsBackend(MetricsBackend):
    """TorchMetrics-based backend implementation."""

    def __init__(self, metrics_info: Union[List[str], Dict[str, Any]]):
        try:
            import torch
            from torchmetrics import Metric
        except ImportError:
            raise ImportError(
                "TorchMetricsBackend requires torch and torchmetrics to be installed."
            )
        self.metric_info = metrics_info
        self.torch = torch
        self.Metric = Metric
        self.validate_metrics_info(metrics_info)

    def validate_metrics_info(self, metrics_info):
        if not isinstance(metrics_info, dict):
            raise TypeError(
                "TorchMetricsBackend requires metrics_info as a dict {name: MetricInstance}"
            )
        for k, v in metrics_info.items():
            if not isinstance(k, str):
                raise TypeError(f"Key '{k}' is not a string")
            if not isinstance(v, self.Metric):
                raise TypeError(f"Value for key '{k}' must be a torchmetrics.Metric")
        return metrics_info

    def compute_metrics(self, metrics_info, metrics_data_dict, *args, **kwargs):
        out_dict = {}
        for metric, metric_instance in metrics_info.items():
            if metric not in metrics_data_dict:
                raise ValueError(f"Metric '{metric}' not found in provided data.")

            metric_data = metrics_data_dict[metric]
            sig = inspect.signature(metric_instance.update)
            expected_args = list(sig.parameters.values())

            if isinstance(metric_data, dict):
                args = [metric_data[param.name] for param in expected_args]
            elif isinstance(metric_data, (list, tuple)):
                args = metric_data
            else:
                raise TypeError(f"Unsupported data format for metric '{metric}'")

            if len(expected_args) == 1:
                metric_instance.update(args)
            else:
                metric_instance.update(*args)

            computed_value = metric_instance.compute()
            if isinstance(computed_value, self.torch.Tensor):
                computed_value = (
                    computed_value.item()
                    if computed_value.numel() == 1
                    else computed_value.tolist()
                )


            out_dict[metric] = computed_value
        return out_dict
