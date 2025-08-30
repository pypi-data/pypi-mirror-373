"""
Distilled - A data stream reduction middleware

Reduces large multivariate data streams to representative subsets while 
maintaining proportional characteristics across time horizons.
"""

from .core import DistilledProcessor, DataPoint
from .grading import GradingFunction, NumericGrader, CategoricalGrader
from .analysis import VectorAnalyzer, ProportionCalculator

__version__ = "0.1.0"
__all__ = [
    "DistilledProcessor", 
    "DataPoint", 
    "GradingFunction", 
    "NumericGrader", 
    "CategoricalGrader",
    "VectorAnalyzer",
    "ProportionCalculator"
] 