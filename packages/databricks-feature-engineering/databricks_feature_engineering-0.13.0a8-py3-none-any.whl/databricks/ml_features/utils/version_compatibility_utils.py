import mlflow
from packaging.version import Version


def _get_target_version(version_str):
    """
    Get the targeting version if the provided version is pre-release version.
    For pre-release libraries, we want to check compatability against their targeting versions. For example,
    This method returns `3.0.0` if given `3.0.0.rc`.
    """
    v = Version(version_str)
    return Version(f"{v.major}.{v.minor}.{v.micro}")


def _current_mlflow_version():
    return _get_target_version(mlflow.__version__)


def is_log_model_artifact_path_deprecated() -> bool:
    deprecation_version = Version("3.0.0")
    return _current_mlflow_version() >= deprecation_version


def mlflow_log_model_starts_run() -> bool:
    change_version = Version("3.0.0")
    return _current_mlflow_version() < change_version
