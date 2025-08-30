"""
Analysis utilities for vector analysis and proportion calculations.

This module provides classes for performing the spatial vector analysis
and proportional representation calculations that drive the selection algorithm.
"""

from typing import Dict, List, Any, Tuple, Union
import numpy as np
from dataclasses import dataclass
from collections import Counter
from copy import deepcopy
from .core import DataPoint


@dataclass
class ProportionGap:
    """
    Represents the gap between current and sent proportions for a variable.
    
    Attributes:
        variable_name: Name of the variable
        category_or_value: Category name (for categorical) or "average" (for numeric)
        current_proportion: Current proportion in overall dataset
        sent_proportion: Proportion in sent data
        gap: Difference (current - sent), positive means underrepresented
        priority: Priority score for selection (smaller gaps get higher priority)
    """
    variable_name: str
    category_or_value: str
    current_proportion: float
    sent_proportion: float
    gap: float
    priority: float


class VectorAnalyzer:
    """
    Performs spatial vector analysis on data points to optimize selection.
    
    This class handles the core algorithm for determining which data points
    will best minimize the representation gaps between current and sent data.
    """
    
    def __init__(self):
        """Initialize the vector analyzer."""
        self.proportion_calculator = ProportionCalculator()
    
    def calculate_representation_gaps(
        self, 
        current_proportions: Dict[str, Dict], 
        sent_proportions: Dict[str, Dict]
    ) -> List[ProportionGap]:
        """
        Calculate representation gaps between current and sent data.
        
        Args:
            current_proportions: Current proportions from all historical data
            sent_proportions: Proportions from previously sent data
            
        Returns:
            List of ProportionGap objects sorted by priority (smallest gaps first)
        """
        gaps = []
        
        for variable_name in current_proportions.keys():
            current_prop = current_proportions[variable_name]
            sent_prop = sent_proportions.get(variable_name, {})
            
            var_type = current_prop.get("type")
            
            if var_type == "categorical":
                # Calculate gaps for each category
                current_categories = current_prop.get("categories", {})
                sent_categories = sent_prop.get("categories", {})
                
                for category, current_proportion in current_categories.items():
                    sent_proportion = sent_categories.get(category, 0.0)
                    gap = current_proportion - sent_proportion
                    
                    # Priority is based on filling underrepresented gaps proportionally
                    # Only consider gaps where current > sent (underrepresented)
                    if gap > 0:
                        # Priority is inversely related to the proportional size of the category
                        # Smaller categories get higher priority to ensure they get represented
                        priority = 1.0 / current_proportion if current_proportion > 0 else 1.0
                    else:
                        priority = -1.0 / current_proportion if current_proportion > 0 else -1.0
                    
                    gaps.append(ProportionGap(
                        variable_name=variable_name,
                        category_or_value=category,
                        current_proportion=current_proportion,
                        sent_proportion=sent_proportion,
                        gap=gap,
                        priority=priority
                    ))


            elif var_type == "numeric":
                # Calculate gap for average values - use actual averages, not normalized
                current_avg = current_prop.get("average", 0.0)
                sent_avg = sent_prop.get("average", 0.0)
                
                # Calculate the absolute difference as the gap
                gap = current_avg - sent_avg
                
                # Priority is based on the magnitude of the gap - larger gaps get higher priority
                priority = abs(gap) if gap != 0 else 0.001
                
                gaps.append(ProportionGap(
                    variable_name=variable_name,
                    category_or_value="average",
                    current_proportion=current_avg,  # Store actual average, not normalized
                    sent_proportion=sent_avg,       # Store actual average, not normalized
                    gap=gap,
                    priority=priority
                ))
            
        gaps.sort(key=lambda g: (g.priority, -g.gap))
        return gaps
    
    def score_candidate_point(
        self, 
        point: DataPoint, 
        gaps: List[ProportionGap],
        current_sent_count: int
    ) -> float:
        """
        Calculate how much a candidate point would improve representation.
        
        Args:
            point: DataPoint to evaluate
            gaps: Current representation gaps
            current_sent_count: Number of points already sent
            
        Returns:
            Score representing improvement potential (higher = better)
        """
        if not point.vector_values:
            return 0.0
        
        total_score = 0.0
        
        # Create a mapping for faster gap lookup
        gap_map = {}
        for gap in gaps:
            key = (gap.variable_name, gap.category_or_value)
            gap_map[key] = gap
        
        for variable_name, value in point.vector_values.items():
            # For categorical variables, find the gap for this specific category
            if isinstance(value, str):
                key = (variable_name, value)
                if key in gap_map:
                    gap = gap_map[key]
                    # Only score positively if this would help close an underrepresented gap
                    if gap.gap > 0:  # Underrepresented
                        # Weight by priority - smaller gaps get more weight
                        improvement = gap.gap / (gap.priority + 0.001)
                        total_score += improvement
            
            # For numeric variables, calculate improvement based on direction
            else:
                key = (variable_name, "average")
                if key in gap_map:
                    gap = gap_map[key]
                    if gap.gap != 0:
                        # Calculate how much this point would move the sent average toward the current average
                        current_sent_avg = gap.sent_proportion  # This is now the actual sent average
                        target_avg = gap.current_proportion     # This is now the actual current average
                        point_value = float(value)
                        
                        # If we need to increase the sent average (gap > 0), prefer higher values
                        # If we need to decrease the sent average (gap < 0), prefer lower values
                        if gap.gap > 0 and point_value > current_sent_avg:
                            # This point would help increase the average
                            improvement = min(abs(point_value - current_sent_avg), abs(gap.gap))
                            total_score += improvement / (gap.priority + 0.001)
                        elif gap.gap < 0 and point_value < current_sent_avg:
                            # This point would help decrease the average
                            improvement = min(abs(current_sent_avg - point_value), abs(gap.gap))
                            total_score += improvement / (gap.priority + 0.001)
        
        return total_score
    
    def select_optimal_points(
        self, 
        candidate_points: List[DataPoint],
        target_count: int,
        current_proportions: Dict[str, Dict],
        sent_proportions: Dict[str, Dict]
    ) -> List[DataPoint]:
        """
        Select the optimal subset of points using greedy algorithm.
        
        Args:
            candidate_points: Available points to choose from
            target_count: Number of points to select
            current_proportions: Current proportions from all data
            sent_proportions: Proportions from sent data
            
        Returns:
            Selected subset of points that best minimizes representation gaps
        """
        if not candidate_points or target_count <= 0:
            return []
        
        # Limit target count to available candidates
        target_count = min(target_count, len(candidate_points))
        
        selected_points = []
        remaining_candidates = candidate_points.copy()
        current_sent_props = deepcopy(sent_proportions)
        current_sent_count = sent_proportions.get('_total_count', 0) if sent_proportions else 0
        
        for selection_round in range(target_count):
            if not remaining_candidates:
                break
            
            # Calculate current representation gaps
            gaps = self.calculate_representation_gaps(current_proportions, current_sent_props)
            
            # Score all remaining candidates
            best_score = -1
            best_candidates = []
            
            for candidate in remaining_candidates:
                score = self.score_candidate_point(candidate, gaps, current_sent_count)
                
                if score > best_score:
                    best_score = score
                    best_candidates = [candidate]
                elif score == best_score and score > 0:
                    best_candidates.append(candidate)
            
            # Handle tie-breaking: prioritize smallest values first
            if len(best_candidates) > 1:
                best_candidate = self._break_ties(best_candidates)
            elif best_candidates:
                best_candidate = best_candidates[0]
            else:
                # If no candidates improve the score, just take the first one
                best_candidate = remaining_candidates[0]
            
            # Select this candidate
            selected_points.append(best_candidate)
            remaining_candidates.remove(best_candidate)
            
            # Update sent proportions simulation for next iteration
            current_sent_props = self.simulate_proportion_update(
                current_sent_props, best_candidate, current_sent_count
            )
            current_sent_count += 1
        
        return selected_points
    
    def simulate_proportion_update(
        self, 
        current_sent_proportions: Dict[str, Dict],
        selected_point: DataPoint,
        total_sent_count: int
    ) -> Dict[str, Dict]:
        """
        Simulate how proportions would change if a point is selected.
        
        Args:
            current_sent_proportions: Current sent data proportions
            selected_point: Point being considered for selection
            total_sent_count: Current count of sent points
            
        Returns:
            Updated proportions after adding the selected point
        """
        if not selected_point.vector_values:
            return deepcopy(current_sent_proportions)
        
        updated_props = deepcopy(current_sent_proportions)
        new_total_count = total_sent_count + 1
        
        for variable_name, value in selected_point.vector_values.items():
            if variable_name not in updated_props:
                # Initialize this variable in sent proportions
                if isinstance(value, str):
                    updated_props[variable_name] = {
                        "type": "categorical",
                        "categories": {value: 1.0},
                        "total_count": 1
                    }
                else:
                    updated_props[variable_name] = {
                        "type": "numeric",
                        "average": float(value),
                        "total_count": 1
                    }
            else:
                # Update existing variable
                var_props = updated_props[variable_name]
                var_type = var_props.get("type")
                
                if var_type == "categorical":
                    # Update categorical counts and proportions
                    categories = var_props.get("categories", {})
                    old_total = var_props.get("total_count", 0)
                    
                    # Add one count for this category
                    old_count = categories.get(value, 0) * old_total
                    new_count = old_count + 1
                    new_total = old_total + 1
                    
                    # Recalculate all proportions
                    updated_categories = {}
                    for cat, old_prop in categories.items():
                        if cat == value:
                            updated_categories[cat] = new_count / new_total
                        else:
                            old_cat_count = old_prop * old_total
                            updated_categories[cat] = old_cat_count / new_total
                    
                    # If this is a new category, add it
                    if value not in categories:
                        updated_categories[value] = 1.0 / new_total
                    
                    var_props["categories"] = updated_categories
                    var_props["total_count"] = new_total
                
                elif var_type == "numeric":
                    # Update numeric average
                    old_avg = var_props.get("average", 0.0)
                    old_total = var_props.get("total_count", 0)
                    
                    # Calculate new average: (old_sum + new_value) / new_count
                    old_sum = old_avg * old_total
                    new_sum = old_sum + float(value)
                    new_total = old_total + 1
                    new_avg = new_sum / new_total if new_total > 0 else float(value)
                    
                    var_props["average"] = new_avg
                    var_props["total_count"] = new_total
        
        # Track total count for future reference
        updated_props['_total_count'] = new_total_count
        
        return updated_props
    
    def _break_ties(self, candidates: List[DataPoint]) -> DataPoint:
        """
        Break ties between equally-scoring candidates using random selection.
        
        Args:
            candidates: List of candidate points with equal scores
            
        Returns:
            Randomly selected candidate to avoid systematic bias
        """
        if len(candidates) == 1:
            return candidates[0]
        
        # Use random selection to break ties to avoid systematic bias toward small/large values
        import random
        return random.choice(candidates)


class ProportionCalculator:
    """
    Calculates and manages proportional representations of data sets.
    
    This class handles the math for computing proportions and averages
    from collections of data points.
    """
    
    def __init__(self):
        """Initialize the proportion calculator."""
        pass
    
    def calculate_proportions(
        self, 
        data_points: List[DataPoint], 
        variable_names: List[str],
        grading_functions: Dict[str, Any]
    ) -> Dict[str, Dict]:
        """
        Calculate proportions/averages for all variables in a dataset.
        
        Args:
            data_points: List of DataPoint objects to analyze
            variable_names: Names of variables to calculate proportions for
            grading_functions: Grading functions to determine categorical vs numeric
            
        Returns:
            Dictionary with structure:
            {
                "variable_name": {
                    "type": "categorical" | "numeric",
                    "categories": {...} | "average": float,
                    "total_count": int
                }
            }
        """
        if not data_points:
            return {}
        
        result = {}
        
        for variable_name in variable_names:
            if variable_name not in grading_functions:
                continue
                
            grader = grading_functions[variable_name]
            
            # Extract values for this variable from all data points
            values = []
            for point in data_points:
                if point.vector_values and variable_name in point.vector_values:
                    values.append(point.vector_values[variable_name])
            
            if not values:
                continue
            
            # Calculate proportions based on whether it's categorical or numeric
            if grader.is_categorical():
                proportions = self.calculate_categorical_proportions(values)
                result[variable_name] = {
                    "type": "categorical",
                    "categories": proportions,
                    "total_count": len(values)
                }
            else:
                # Convert to float list for numeric calculation
                numeric_values = [float(v) for v in values]
                average = self.calculate_numeric_average(numeric_values)
                result[variable_name] = {
                    "type": "numeric", 
                    "average": average,
                    "total_count": len(values)
                }
        
        return result
    
    def calculate_categorical_proportions(
        self, 
        values: List[str]
    ) -> Dict[str, float]:
        """
        Calculate proportions for categorical values.
        
        Args:
            values: List of categorical values
            
        Returns:
            Dictionary mapping categories to their proportions (0.0 to 1.0)
        """
        if not values:
            return {}
        
        # Count occurrences of each category
        counts = Counter(values)
        total = len(values)
        
        # Calculate proportions
        proportions = {}
        for category, count in counts.items():
            proportions[category] = count / total
        
        return proportions
    
    def calculate_numeric_average(self, values: List[float]) -> float:
        """
        Calculate average for numeric values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Average value
        """
        if not values:
            return 0.0
        
        return sum(values) / len(values)
    
    def merge_proportions(
        self, 
        props1: Dict[str, Dict], 
        props2: Dict[str, Dict],
        weight1: float = 0.5,
        weight2: float = 0.5
    ) -> Dict[str, Dict]:
        """
        Merge two proportion dictionaries with weighting.
        
        Args:
            props1: First proportion dictionary
            props2: Second proportion dictionary  
            weight1: Weight for first dictionary (default 0.5)
            weight2: Weight for second dictionary (default 0.5)
            
        Returns:
            Merged proportion dictionary
        """
        if not props1:
            return deepcopy(props2)
        if not props2:
            return deepcopy(props1)
        
        # Ensure weights sum to 1.0
        total_weight = weight1 + weight2
        if total_weight > 0:
            weight1 = weight1 / total_weight
            weight2 = weight2 / total_weight
        else:
            weight1 = weight2 = 0.5
        
        result = {}
        all_variables = set(props1.keys()) | set(props2.keys())
        
        for variable in all_variables:
            prop1 = props1.get(variable, {})
            prop2 = props2.get(variable, {})
            
            # Skip if neither has this variable
            if not prop1 and not prop2:
                continue
            
            # If only one has this variable, use it directly
            if not prop1:
                result[variable] = deepcopy(prop2)
                continue
            if not prop2:
                result[variable] = deepcopy(prop1)
                continue
            
            # Both have this variable - merge based on type
            var_type = prop1.get("type", prop2.get("type"))
            
            if var_type == "categorical":
                # Merge categorical proportions
                all_categories = set()
                if "categories" in prop1:
                    all_categories.update(prop1["categories"].keys())
                if "categories" in prop2:
                    all_categories.update(prop2["categories"].keys())
                
                merged_categories = {}
                for category in all_categories:
                    val1 = prop1.get("categories", {}).get(category, 0.0)
                    val2 = prop2.get("categories", {}).get(category, 0.0)
                    merged_categories[category] = val1 * weight1 + val2 * weight2
                
                result[variable] = {
                    "type": "categorical",
                    "categories": merged_categories,
                    "total_count": prop1.get("total_count", 0) + prop2.get("total_count", 0)
                }
            
            elif var_type == "numeric":
                # Merge numeric averages
                avg1 = prop1.get("average", 0.0)
                avg2 = prop2.get("average", 0.0)
                merged_average = avg1 * weight1 + avg2 * weight2
                
                result[variable] = {
                    "type": "numeric",
                    "average": merged_average,
                    "total_count": prop1.get("total_count", 0) + prop2.get("total_count", 0)
                }
        
        return result
    
    def proportions_distance(
        self, 
        props1: Dict[str, Dict], 
        props2: Dict[str, Dict]
    ) -> float:
        """
        Calculate distance between two proportion dictionaries.
        
        Args:
            props1: First proportion dictionary
            props2: Second proportion dictionary
            
        Returns:
            Distance metric (0.0 = identical, higher = more different)
        """
        if not props1 and not props2:
            return 0.0
        if not props1 or not props2:
            return float('inf')  # Maximum distance if one is empty
        
        total_distance = 0.0
        all_variables = set(props1.keys()) | set(props2.keys())
        
        for variable in all_variables:
            prop1 = props1.get(variable, {})
            prop2 = props2.get(variable, {})
            
            # If variable missing from one side, add penalty
            if not prop1 or not prop2:
                total_distance += 1.0
                continue
            
            var_type = prop1.get("type", prop2.get("type"))
            
            if var_type == "categorical":
                # Calculate sum of squared differences for categories
                all_categories = set()
                if "categories" in prop1:
                    all_categories.update(prop1["categories"].keys())
                if "categories" in prop2:
                    all_categories.update(prop2["categories"].keys())
                
                category_distance = 0.0
                for category in all_categories:
                    val1 = prop1.get("categories", {}).get(category, 0.0)
                    val2 = prop2.get("categories", {}).get(category, 0.0)
                    category_distance += (val1 - val2) ** 2
                
                total_distance += category_distance
            
            elif var_type == "numeric":
                # Calculate squared difference of averages
                avg1 = prop1.get("average", 0.0)
                avg2 = prop2.get("average", 0.0)
                # Normalize by dividing by max to keep scale reasonable
                max_avg = max(abs(avg1), abs(avg2), 1.0)
                normalized_distance = ((avg1 - avg2) / max_avg) ** 2
                total_distance += normalized_distance
        
        return total_distance 