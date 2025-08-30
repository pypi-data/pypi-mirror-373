import inspect
import os
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlparse
import mlflow
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any


def normalize_artifact_uri(artifact_uri: str) -> str:
    """
    Normalize the artifact URI to a standard file path.

    Args:
        artifact_uri (str): The artifact URI to normalize.

    Returns:
        str: The normalized file path.
    """
    if artifact_uri.startswith("file:///"):
        parsed_uri = urlparse(artifact_uri)
        return os.path.abspath(os.path.join(parsed_uri.path.lstrip('/')))
    return artifact_uri

class Tracking(ABC):
    def __init__(self,  experiment_name: str, tracking_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the tracking backend.

        Args:
            experiment_name (str): The name of the experiment.
            experiment_tags (dict, optional): Tags for the experiment.
        """
        self.experiment_name = experiment_name
        self.tracking_params = tracking_params or {}

    @abstractmethod
    def setup_experiment(self):
        """Set up the experiment in the tracking backend."""
        pass

    @abstractmethod
    def run(self, run_name: str, description:str, func: Callable, nested_run: bool = False):
        """Run the experiment with the given function."""
        pass

    @abstractmethod
    def log_text(self, content:str, file_name: str):
        """Log parameters to the tracking backend."""
        pass
    @abstractmethod
    def log_param(self, key:str, value: Any):
        """Log parameters to the tracking backend."""
        pass
    @abstractmethod
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to the tracking backend."""
        pass

    @abstractmethod
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to the tracking backend."""
        pass

    @abstractmethod
    def log_artifact(self, artifact_path: str):
        """Log an artifact to the tracking backend."""
        pass


logger = logging.getLogger(__name__)


class MLFlowTracking(Tracking):
    def __init__(self, experiment_name: str, tracking_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the MLFlowTracking backend.

        Args:
            experiment_name (str): The name of the experiment.
            tracking_params (dict, optional): Parameters for MLflow tracking.
        """
        super().__init__(experiment_name, tracking_params)
        if tracking_params:
            self.experiment_tags = tracking_params.get("experiment_tags", {})

    def setup_experiment(self):
        """Set up an experiment in MLflow."""
        tracking_uri = self.tracking_params.get("tracking_uri")
        if not tracking_uri:
            raise ValueError("Tracking URI must be specified for MLflow.")

        mlflow.set_tracking_uri(tracking_uri)

        if mlflow.get_experiment_by_name(self.experiment_name) is None:
            artifact_location = self.tracking_params.get("artifact_location")
            mlflow.create_experiment(self.experiment_name, artifact_location)
            logger.info(
                f"Created new MLflow experiment: {self.experiment_name}")

        mlflow.set_experiment(self.experiment_name)

        if self.experiment_tags:
            mlflow.set_experiment_tags(self.experiment_tags)
            logger.info(
                f"Set tags for MLflow experiment '{self.experiment_name}': {self.experiment_tags}")

    def run(self, run_name: str, description:str, func: Callable, nested_run: bool = False):
        """Run the experiment with the given function."""
        func_signature = inspect.signature(func)
       
        if nested_run:
            with mlflow.start_run(run_name=run_name, description= description, nested=True) as run:
                if "artifact_uri" in func_signature.parameters:
                    artifact_uri = normalize_artifact_uri(run.info.artifact_uri) if run.info.artifact_uri else ""
                    return func(artifact_uri=artifact_uri)
                else:
                    return func()
        else:
            with mlflow.start_run(run_name=run_name, description= description) as run:
                 if "artifact_uri" in func_signature.parameters:
                    artifact_uri = normalize_artifact_uri(run.info.artifact_uri) if run.info.artifact_uri else ""
                    return func(artifact_uri=artifact_uri)
                 else:
                    return func()
    
    def log_text(self, content: str, file_name: str):
        mlflow.log_text(
            content, artifact_file=file_name)
    
    def log_param(self, key: str, value: Any):
         mlflow.log_param(key, value)

    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow."""
        mlflow.log_params(params)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow."""
        mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, artifact_path: str):
        """Log an artifact to MLflow."""
        mlflow.log_artifact(artifact_path)


class TrackingService:
    def __init__(self, experiment_name: str, backend: str = "mlflow", tracking_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the TrackingService.

        Args:
            backend (str): The tracking backend to use (e.g., "mlflow").
            tracking_params (dict, optional): Parameters for the tracking backend.
        """
        self.experiment_name = experiment_name
        self.backend = backend.lower()
        self.tracking_params = tracking_params or {}
        self.tracking_instance = self._initialize_backend()

    def _initialize_backend(self) -> Tracking:
        """Initialize the appropriate tracking backend."""
        if self.backend == "mlflow":
            return MLFlowTracking(self.experiment_name, self.tracking_params)
        else:
            raise ValueError(f"Unsupported tracking backend: {self.backend}")

    def setup(self):
        """Set up the experiment in the tracking backend."""
        self.tracking_instance.setup_experiment()

    def run(self, run_name: str, description:str ,func: Callable, nested_run: bool = False) -> Any:
        """Run the experiment with the given function."""
        return self.tracking_instance.run(run_name, description , func, nested_run=nested_run)
        
    def log_text(self, content: str, file_name: str):
        self.tracking_instance.log_text(content, file_name)
        
    def log_param(self, key: str, value: Any):
        """Log a parameter to the tracking backend."""
        self.tracking_instance.log_param(key, value)

    def log_params(self, params: Dict[str, Any]):
        """Log parameters to the tracking backend."""
        self.tracking_instance.log_params(params)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to the tracking backend."""
        self.tracking_instance.log_metrics(metrics, step=step)

    def log_artifact(self, artifact_path: str):
        """Log an artifact to the tracking backend."""
        self.tracking_instance.log_artifact(artifact_path)
