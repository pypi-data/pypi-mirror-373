"""
Grading functions for evaluating data point characteristics.

This module provides the base classes and implementations for functions that
evaluate data points and convert them to vector values for analysis.
"""

from abc import ABC, abstractmethod
from typing import Any, Union, List, Callable


class GradingFunction(ABC):
    """
    Abstract base class for grading functions.
    
    Grading functions take a data point and return either a numerical value
    or a categorical string that represents one aspect of the data point.
    """
    
    def __init__(self, name: str):
        """
        Initialize the grading function.
        
        Args:
            name: Human-readable name for this grading function
        """
        self.name = name
    
    @abstractmethod
    def evaluate(self, data_point: Any) -> Union[float, str]:
        """
        Evaluate a data point and return its graded value.
        
        Args:
            data_point: The raw data point to evaluate
            
        Returns:
            Either a float (for numerical characteristics) or 
            a string (for categorical characteristics)
        """
        pass
    
    @abstractmethod
    def is_categorical(self) -> bool:
        """
        Return whether this grading function produces categorical values.
        
        Returns:
            True if this function returns categorical strings,
            False if it returns numerical values
        """
        pass


class NumericGrader(GradingFunction):
    """
    Grading function that produces numerical values.
    
    This class wraps a user-provided function that extracts numerical
    characteristics from data points.
    """
    
    def __init__(self, name: str, extractor_func: Callable[[Any], float]):
        """
        Initialize the numeric grader.
        
        Args:
            name: Human-readable name for this grading function
            extractor_func: Function that takes a data point and returns a float
        """
        super().__init__(name)
        self.extractor_func = extractor_func
    
    def evaluate(self, data_point: Any) -> float:
        """
        Evaluate a data point and return its numerical value.
        
        Args:
            data_point: The raw data point to evaluate
            
        Returns:
            Float value representing this characteristic
        """
        try:
            result = self.extractor_func(data_point)
            if not isinstance(result, (int, float)):
                raise ValueError(f"Extractor function for '{self.name}' returned {type(result)}, expected numeric value")
            return float(result)
        except Exception as e:
            raise ValueError(f"Error evaluating numeric grader '{self.name}': {str(e)}") from e
    
    def is_categorical(self) -> bool:
        """Return False since this produces numerical values."""
        return False


class CategoricalGrader(GradingFunction):
    """
    Grading function that produces categorical values from a predefined list.
    
    This class wraps a user-provided function that classifies data points
    into one of several predefined categories.
    """
    
    def __init__(
        self, 
        name: str, 
        categories: List[str], 
        classifier_func: Callable[[Any], str]
    ):
        """
        Initialize the categorical grader.
        
        Args:
            name: Human-readable name for this grading function
            categories: List of valid category strings
            classifier_func: Function that takes a data point and returns a category string
        """
        super().__init__(name)
        self.categories = categories
        self.classifier_func = classifier_func
        
        if not categories:
            raise ValueError(f"Categories list for '{name}' cannot be empty")
        
        # Convert to set for faster lookup
        self._category_set = set(categories)
    
    def evaluate(self, data_point: Any) -> str:
        """
        Evaluate a data point and return its category.
        
        Args:
            data_point: The raw data point to evaluate
            
        Returns:
            String category from the predefined categories list
        """
        try:
            result = self.classifier_func(data_point)
            if not isinstance(result, str):
                raise ValueError(f"Classifier function for '{self.name}' returned {type(result)}, expected string")
            
            if result not in self._category_set:
                raise ValueError(f"Classifier function for '{self.name}' returned '{result}', which is not in valid categories: {self.categories}")
            
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating categorical grader '{self.name}': {str(e)}") from e
    
    def is_categorical(self) -> bool:
        """Return True since this produces categorical values."""
        return True
    
    def get_categories(self) -> List[str]:
        """
        Get the list of valid categories for this grader.
        
        Returns:
            List of valid category strings
        """
        return self.categories.copy()


class LambdaGrader(GradingFunction):
    """
    Simple grader that wraps a lambda function or simple callable.
    
    This is a convenience class for quick grading function creation
    without needing to subclass GradingFunction.
    """
    
    def __init__(
        self, 
        name: str, 
        func: Callable[[Any], Union[float, str]], 
        is_categorical: bool = False,
        categories: List[str] = None
    ):
        """
        Initialize the lambda grader.
        
        Args:
            name: Human-readable name for this grading function
            func: Function that takes a data point and returns a value
            is_categorical: Whether this function returns categorical values
            categories: List of valid categories (required if is_categorical=True)
        """
        super().__init__(name)
        self.func = func
        self._is_categorical = is_categorical
        self.categories = categories or []
        
        if is_categorical and not categories:
            raise ValueError("categories must be provided when is_categorical=True")
        
        if is_categorical:
            self._category_set = set(categories)
    
    def evaluate(self, data_point: Any) -> Union[float, str]:
        """
        Evaluate a data point using the wrapped function.
        
        Args:
            data_point: The raw data point to evaluate
            
        Returns:
            Result from the wrapped function
        """
        try:
            result = self.func(data_point)
            
            if self._is_categorical:
                if not isinstance(result, str):
                    raise ValueError(f"Lambda function for '{self.name}' returned {type(result)}, expected string for categorical grader")
                
                if result not in self._category_set:
                    raise ValueError(f"Lambda function for '{self.name}' returned '{result}', which is not in valid categories: {self.categories}")
                
                return result
            else:
                if not isinstance(result, (int, float)):
                    raise ValueError(f"Lambda function for '{self.name}' returned {type(result)}, expected numeric value")
                
                return float(result)
                
        except Exception as e:
            raise ValueError(f"Error evaluating lambda grader '{self.name}': {str(e)}") from e
    
    def is_categorical(self) -> bool:
        """Return whether this grader produces categorical values."""
        return self._is_categorical


def create_grading_functions(config: dict) -> dict:
    """
    Factory function to create grading functions from configuration.
    
    Args:
        config: Dictionary defining grading functions. Format:
            {
                "variable_name": {
                    "type": "numeric" | "categorical" | "lambda",
                    "function": callable,
                    "categories": [...] (for categorical only)
                }
            }
    
    Returns:
        Dictionary mapping variable names to GradingFunction instances
    """
    grading_functions = {}
    
    for variable_name, spec in config.items():
        # Validate required fields
        if not isinstance(spec, dict):
            raise ValueError(f"Configuration for '{variable_name}' must be a dictionary")
        
        if "type" not in spec:
            raise ValueError(f"Configuration for '{variable_name}' must specify 'type'")
        
        if "function" not in spec:
            raise ValueError(f"Configuration for '{variable_name}' must specify 'function'")
        
        func_type = spec["type"]
        func = spec["function"]
        
        if not callable(func):
            raise ValueError(f"Function for '{variable_name}' must be callable")
        
        # Create appropriate grading function based on type
        if func_type == "numeric":
            grading_functions[variable_name] = NumericGrader(
                name=variable_name,
                extractor_func=func
            )
        
        elif func_type == "categorical":
            if "categories" not in spec:
                raise ValueError(f"Categorical configuration for '{variable_name}' must specify 'categories'")
            
            categories = spec["categories"]
            if not isinstance(categories, list):
                raise ValueError(f"Categories for '{variable_name}' must be a list")
            
            grading_functions[variable_name] = CategoricalGrader(
                name=variable_name,
                categories=categories,
                classifier_func=func
            )
        
        elif func_type == "lambda":
            is_categorical = spec.get("is_categorical", False)
            categories = spec.get("categories", [])
            
            if is_categorical and not categories:
                raise ValueError(f"Lambda configuration for '{variable_name}' must specify 'categories' when is_categorical=True")
            
            grading_functions[variable_name] = LambdaGrader(
                name=variable_name,
                func=func,
                is_categorical=is_categorical,
                categories=categories
            )
        
        else:
            raise ValueError(f"Unknown function type '{func_type}' for '{variable_name}'. Must be 'numeric', 'categorical', or 'lambda'")
    
    return grading_functions