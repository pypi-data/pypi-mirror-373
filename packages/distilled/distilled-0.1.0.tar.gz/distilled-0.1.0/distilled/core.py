"""
Core classes for the Distilled data stream reduction system.

This module contains the main DistilledProcessor class and supporting data structures.
"""

from typing import Dict, List, Any, Generator, Optional, Callable, Union
from collections import deque
from dataclasses import dataclass
import time


@dataclass
class DataPoint:
    """
    Represents a single data point in the stream with its raw data and metadata.
    
    Attributes:
        data: The raw data payload (dict, object, etc.)
        timestamp: When this data point was received
        vector_values: Cached vector values after grading function evaluation
        sent_previously: Whether this point was previously sent downstream
    """
    data: Any
    timestamp: float
    vector_values: Optional[Dict[str, Union[float, str]]] = None
    sent_previously: bool = False


class DistilledProcessor:
    """
    Main processor for reducing multivariate data streams while maintaining proportional representation.
    
    This class implements a generator/coroutine pattern that:
    1. Accepts batches of data points
    2. Evaluates them using configurable grading functions
    3. Maintains sliding time window of historical data
    4. Selects optimal 10% subset that preserves proportional characteristics
    5. Yields selected points for downstream processing
    
    The processor uses spatial vector analysis and A/B testing strategies to ensure
    the selected subset accurately represents the full dataset's characteristics.
    """
    
    def __init__(
        self,
        grading_functions: Dict[str, Callable],
        time_horizon_seconds: int = 3600,
        reduction_percentage: float = 0.1,
        batch_size: int = 100
    ):
        """
        Initialize the DistilledProcessor.
        
        Args:
            grading_functions: Dict mapping variable names to functions that evaluate
                             data points. Functions should return either float or 
                             categorical string values.
            time_horizon_seconds: How long to maintain historical data (60-3600 seconds)
            reduction_percentage: What percentage of data to pass through (default 0.1 = 10%)
            batch_size: How many points to process at once (default 100)
        """
        self.grading_functions = grading_functions
        self.time_horizon_seconds = time_horizon_seconds
        self.reduction_percentage = reduction_percentage
        self.batch_size = batch_size
        
        # FIFO queue for all data points within time horizon
        self.historical_data: deque = deque()
        
        # FIFO queue for previously sent data points within time horizon
        self.sent_data: deque = deque()
        
        # Track current proportions and statistics
        self.current_proportions: Dict[str, Dict] = {}
        self.sent_proportions: Dict[str, Dict] = {}
        
        # Import analysis components
        from .analysis import VectorAnalyzer, ProportionCalculator
        self.vector_analyzer = VectorAnalyzer()
        self.proportion_calculator = ProportionCalculator()
        
        # Generator state
        self._generator = None
        self._initialize_generator()

    def _initialize_generator(self) -> None:
        """Initialize the internal generator coroutine."""
        self._generator = self._process_stream()
        next(self._generator)  # Prime the generator

    def process_batch(self, data_points: List[Any]) -> List[DataPoint]:
        """
        Process a batch of data points and return the selected subset.
        
        Args:
            data_points: List of raw data points to process
            
        Returns:
            List of selected DataPoint objects that best maintain proportional representation over the time horizon
        """
        return self._generator.send(data_points)

    def _process_stream(self) -> Generator[List[DataPoint], List[Any], None]:
        """
        Main generator coroutine that processes the data stream.
        
        This implements the core algorithm:
        1. Receive batch of data points
        2. Convert to DataPoint objects with vector evaluation
        3. Update historical data with time horizon management
        4. Calculate current vs sent proportions
        5. Select optimal subset using vector analysis
        6. Update sent data tracking
        7. Yield selected points
        """
        result = []  # Initial result
        
        while True:
            # Receive batch from caller and yield previous result
            raw_batch = yield result
            
            # Convert to DataPoint objects and evaluate vectors
            batch_points = self._create_data_points(raw_batch)
            
            # Update historical data with time-based cleanup
            self._update_historical_data(batch_points)
            
            # Calculate current proportions from all historical data
            self._calculate_current_proportions()
            
            # Calculate proportions of previously sent data
            self._calculate_sent_proportions()
            
            # Select optimal subset using vector analysis
            selected_points = self._select_optimal_subset(batch_points)
            
            # Update sent data tracking
            self._update_sent_data(selected_points)
            
            # Set result for next yield
            result = selected_points

    def _create_data_points(self, raw_data: List[Any]) -> List[DataPoint]:
        """
        Convert raw data to DataPoint objects with vector evaluation.
        
        Args:
            raw_data: List of raw data objects
            
        Returns:
            List of DataPoint objects with evaluated vector values
        """
        current_time = time.time()
        data_points = []
        
        for raw_item in raw_data:
            # Create DataPoint with current timestamp
            point = DataPoint(
                data=raw_item,
                timestamp=current_time,
                vector_values={},
                sent_previously=False
            )
            
            # Apply each grading function to get vector values
            for variable_name, grading_function in self.grading_functions.items():
                try:
                    value = grading_function.evaluate(raw_item)
                    point.vector_values[variable_name] = value
                except Exception as e:
                    # Log error and skip this variable for this point
                    print(f"Warning: Failed to evaluate {variable_name} for data point: {e}")
                    continue
            
            data_points.append(point)
        
        return data_points

    def _update_historical_data(self, new_points: List[DataPoint]) -> None:
        """
        Add new points to historical data and remove expired points.
        
        Args:
            new_points: New DataPoint objects to add to history
        """
        current_time = time.time()
        
        # Add new points to the right side of the deque
        for point in new_points:
            self.historical_data.append(point)
        
        # Remove expired points from the left side
        self._cleanup_expired_data(current_time)

    def _calculate_current_proportions(self) -> None:
        """
        Calculate current proportions/averages for all variables from historical data.
        
        Updates self.current_proportions with:
        - Categorical variables: percentage breakdown per category
        - Numerical variables: running averages
        """
        if not self.historical_data:
            self.current_proportions = {}
            return
        
        # Convert deque to list for proportion calculation
        data_points = list(self.historical_data)
        variable_names = list(self.grading_functions.keys())
        
        self.current_proportions = self.proportion_calculator.calculate_proportions(
            data_points, variable_names, self.grading_functions
        )

    def _calculate_sent_proportions(self) -> None:
        """
        Calculate proportions/averages for previously sent data within time horizon.
        
        Updates self.sent_proportions with same structure as current_proportions.
        """
        if not self.sent_data:
            self.sent_proportions = {}
            return
        
        # Convert deque to list for proportion calculation
        data_points = list(self.sent_data)
        variable_names = list(self.grading_functions.keys())
        
        self.sent_proportions = self.proportion_calculator.calculate_proportions(
            data_points, variable_names, self.grading_functions
        )

    def _select_optimal_subset(self, candidate_points: List[DataPoint]) -> List[DataPoint]:
        """
        Select the optimal subset of points that best maintains proportional representation.
        
        This implements the core selection algorithm:
        1. Calculate representation gaps (current - sent proportions)
        2. For each candidate point, calculate its impact on closing gaps
        3. Select points that bring underrepresented buckets closer to target
        4. Prioritize smallest proportional buckets first
        5. Handle ties by favoring smallest values
        
        Args:
            candidate_points: Available points to choose from
            
        Returns:
            Selected subset of points (typically 10% of input)
        """
        if not candidate_points:
            return []
        
        # Calculate target number of points to select
        target_count = max(1, int(len(candidate_points) * self.reduction_percentage))
        
        # Use vector analyzer to select optimal points
        selected_points = self.vector_analyzer.select_optimal_points(
            candidate_points=candidate_points,
            target_count=target_count,
            current_proportions=self.current_proportions,
            sent_proportions=self.sent_proportions
        )
        
        return selected_points

    def _update_sent_data(self, selected_points: List[DataPoint]) -> None:
        """
        Update the sent data tracking with newly selected points.
        
        Args:
            selected_points: Points that are being sent downstream
        """
        current_time = time.time()
        
        # Mark selected points as sent and add to sent_data deque
        for point in selected_points:
            point.sent_previously = True
            self.sent_data.append(point)
        
        # Remove expired sent data points
        self._cleanup_expired_data(current_time)

    def _cleanup_expired_data(self, current_time: float) -> None:
        """
        Remove data points that are older than the time horizon.
        
        Args:
            current_time: Current timestamp for age calculation
        """
        # Remove expired historical data points from the left side
        while self.historical_data:
            oldest_point = self.historical_data[0]
            if current_time - oldest_point.timestamp > self.time_horizon_seconds:
                self.historical_data.popleft()
            else:
                break  # Since deque is ordered, we can stop here
        
        # Remove expired sent data points from the left side
        while self.sent_data:
            oldest_point = self.sent_data[0]
            if current_time - oldest_point.timestamp > self.time_horizon_seconds:
                self.sent_data.popleft()
            else:
                break

    def get_current_stats(self) -> Dict[str, Any]:
        """
        Get current statistics about the processor state.
        
        Returns:
            Dictionary containing current proportions, sent proportions, 
            data counts, and other diagnostic information
        """
        return {
            "current_proportions": self.current_proportions.copy(),
            "sent_proportions": self.sent_proportions.copy(),
            "historical_data_count": len(self.historical_data),
            "sent_data_count": len(self.sent_data),
            "time_horizon_seconds": self.time_horizon_seconds,
            "reduction_percentage": self.reduction_percentage,
            "grading_function_count": len(self.grading_functions),
            "grading_function_names": list(self.grading_functions.keys())
        }

    def reset(self) -> None:
        """
        Reset the processor state, clearing all historical data.
        """
        # Clear all deques
        self.historical_data.clear()
        self.sent_data.clear()
        
        # Reset proportion tracking
        self.current_proportions = {}
        self.sent_proportions = {}
        
        # Reinitialize generator
        self._initialize_generator() 