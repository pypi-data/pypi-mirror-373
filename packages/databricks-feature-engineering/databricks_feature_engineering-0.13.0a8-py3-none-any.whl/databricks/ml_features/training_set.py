"""
Backward compatibility module for TrainingSet.

This module provides backward compatibility by importing TrainingSet from its new location
in entities. New code should import directly from databricks.ml_features.entities.training_set
"""

from databricks.ml_features.entities.training_set import TrainingSet

__all__ = ["TrainingSet"]
