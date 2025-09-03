import sys

import mlflow
from enpi_api.l2.util.env import get_mlflow_host


def configure_enpi_mlflow(force: bool = False) -> None:
    if mlflow.is_tracking_uri_set() and not force:
        # Print to stderr to avoid breaking the API
        print("MLflow is already configured, skipping", file=sys.stderr)
        return

    # We only need to set the tracking URI, the artifact and registry URIs are set automatically
    mlflow.set_tracking_uri(uri=get_mlflow_host())
