import warnings
from collections import Counter
from functools import wraps
from typing import Any, List

from mlflow.store.artifact.models_artifact_repo import ModelsArtifactRepository
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository


def is_artifact_uri(uri):
    """
    Checks the artifact URI is associated with a MLflow model or run.
    The actual URI can be a model URI, model URI + subdirectory, or model URI + path to artifact file.
    """
    return ModelsArtifactRepository.is_models_uri(
        uri
    ) or RunsArtifactRepository.is_runs_uri(uri)


def get_duplicates(elements: List[Any]) -> List[Any]:
    """
    Returns duplicate elements in the order they first appear.
    """
    element_counts = Counter(elements)
    duplicates = []
    for e in element_counts.keys():
        if element_counts[e] > 1:
            duplicates.append(e)
    return duplicates


def validate_strings_unique(strings: List[str], error_template: str):
    """
    Validates all strings are unique, otherwise raise ValueError with the error template and duplicates.
    Passes single-quoted, comma delimited duplicates to the error template.
    """
    duplicate_strings = get_duplicates(strings)
    if duplicate_strings:
        duplicates_formatted = ", ".join([f"'{s}'" for s in duplicate_strings])
        raise ValueError(error_template.format(duplicates_formatted))


def get_unique_list_order(elements: List[Any]) -> List[Any]:
    """
    Returns unique elements in the order they first appear.
    """
    return list(dict.fromkeys(elements))


_DEPRECATED_MARK_ATTR_NAME = "__deprecated"


def mark_deprecated(func):
    """
    Mark a function as deprecated by setting a private attribute on it.
    """
    setattr(func, _DEPRECATED_MARK_ATTR_NAME, True)


def is_marked_deprecated(func):
    """
    Is the function marked as deprecated.
    """
    return getattr(func, _DEPRECATED_MARK_ATTR_NAME, False)


def deprecated(alternative=None, since=None, impact=None):
    """
    Annotation decorator for marking APIs as deprecated in docstrings and raising a warning if
    called.
    :param alternative: (Optional string) The name of a superseded replacement function, method,
                        or class to use in place of the deprecated one.
    :param since: (Optional string) A version designator defining during which release the function,
                  method, or class was marked as deprecated.
    :param impact: (Optional boolean) Indication of whether the method, function, or class will be
                   removed in a future release.
    :return: Decorated function.

    TODO[ML-35177]: Migrate change back to mlflow. Changes:
      - Marks the decorated function with attribute `__deprecated`
    """

    def deprecated_decorator(func):
        since_str = " since %s" % since if since else ""
        impact_str = (
            impact if impact else "This method will be removed in a future release."
        )

        notice = (
            "``{qual_function_name}`` is deprecated{since_string}. {impact}".format(
                qual_function_name=".".join([func.__module__, func.__qualname__]),
                since_string=since_str,
                impact=impact_str,
            )
        )
        if alternative is not None and alternative.strip():
            notice += " Use ``%s`` instead." % alternative

        @wraps(func)
        def deprecated_func(*args, **kwargs):
            warnings.warn(notice, category=FutureWarning, stacklevel=2)
            return func(*args, **kwargs)

        if func.__doc__ is not None:
            deprecated_func.__doc__ = ".. Warning:: " + notice + "\n" + func.__doc__

        mark_deprecated(deprecated_func)

        return deprecated_func

    return deprecated_decorator
