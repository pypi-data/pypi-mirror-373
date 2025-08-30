"""
Visual analysis example for Distilled data stream reduction.

This example creates a focused 2-panel visualization:
- Left: Age vs Income scatter plot with color-coded dimensions (Yellow=Gender, Blue=Location)
- Right: Time series of batch averages showing how well targets are tracked

Color encoding maps categorical values proportionally:
- 3 categories: [0, 128, 255] distributed as requested
- Yellow channel represents Gender (Male=0, Female=128, Other=255)
- Blue channel represents Location (Urban=0, Suburban=128, Rural=255)
"""

import sys
import os
# Add the parent directory to Python path so we can import distilled
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distilled import DistilledProcessor, NumericGrader, CategoricalGrader
import random
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import numpy as np
from typing import Dict, Any, List
from collections import deque


# Sample data structure (same as basic_usage.py)
class PersonData:
    """Sample data point representing a person with multiple characteristics."""
    
    def __init__(self, age: int, gender: str, income: float, location: str):
        self.age = age
        self.gender = gender
        self.income = income
        self.location = location
    
    def __repr__(self):
        return f"Person(age={self.age}, gender={self.gender}, income={self.income}, location={self.location})"


def create_sample_grading_functions() -> Dict[str, Any]:
    """Create sample grading functions for person data."""
    
    # Numeric grader for age
    age_grader = NumericGrader(
        name="age",
        extractor_func=lambda person: float(person.age)
    )
    
    # Numeric grader for income
    income_grader = NumericGrader(
        name="income", 
        extractor_func=lambda person: person.income
    )
    
    # Categorical grader for gender (simplified to just male/female)
    gender_grader = CategoricalGrader(
        name="gender",
        categories=["male", "female"],
        classifier_func=lambda person: person.gender.lower()
    )
    
    # Categorical grader for location
    location_grader = CategoricalGrader(
        name="location",
        categories=["urban", "suburban", "rural"],
        classifier_func=lambda person: person.location.lower()
    )
    
    return {
        "age": age_grader,
        "income": income_grader,
        "gender": gender_grader,
        "location": location_grader
    }


def generate_sample_data(count: int, batch_num: int = 1) -> list:
    """Generate sample person data with cyclical oscillating distributions over time."""
    import math
    
    # Use actual time for continuous oscillations
    current_time = time.time()
    
    # Gender distribution oscillates with long periods (simplified to male/female)
    # Male: 50% ± 20% with 8-minute period
    # Female: 50% ± 20% with 6-minute period (different phase)
    male_pct = max(0.2, min(0.8, 0.5 + 0.2 * math.sin(current_time * 2 * math.pi / 480)))
    female_pct = 1.0 - male_pct  # Ensure they sum to 1.0
    
    # Location distribution with different long wave patterns
    # Urban: 40% ± 20% with 10-minute period (10 time horizons)
    # Suburban: 30% ± 12% with 7-minute period (7 time horizons)
    # Rural: 30% ± 18% with 15-minute period (15 time horizons)
    urban_pct = max(0.15, min(0.65, 0.4 + 0.2 * math.cos(current_time * 2 * math.pi / 600)))
    suburban_pct = max(0.15, min(0.45, 0.3 + 0.12 * math.sin(current_time * 2 * math.pi / 420 + math.pi/4)))  
    rural_pct = max(0.1, min(0.55, 0.3 + 0.18 * math.sin(current_time * 2 * math.pi / 900 + math.pi/2)))
    
    # Normalize location percentages
    total_location = urban_pct + suburban_pct + rural_pct
    urban_pct /= total_location
    suburban_pct /= total_location
    rural_pct /= total_location
    
    # Age oscillates: 45 ± 12 years with 9-minute period (9 time horizons)
    base_age = 45 + 12 * math.sin(current_time * 2 * math.pi / 540)
    age_range_low = max(18, int(base_age - 25))
    age_range_high = min(85, int(base_age + 25))
    
    # Income oscillates with different pattern: center moves, range stays similar
    # Center: $85k ± $30k with 11-minute period (11 time horizons)
    # Range: ±$40k around center
    income_center = 85000 + 30000 * math.cos(current_time * 2 * math.pi / 660 + math.pi/6)
    income_low = max(25000, income_center - 40000)
    income_high = income_center + 40000
    
    # Generate weighted random choices for categories
    gender_choices = random.choices(
        ["male", "female"],
        weights=[male_pct, female_pct],
        k=count
    )
    
    location_choices = random.choices(
        ["urban", "suburban", "rural"],
        weights=[urban_pct, suburban_pct, rural_pct],
        k=count
    )
    
    data = []
    for i in range(count):
        # Generate age with bias toward the shifting mean
        age = max(age_range_low, min(age_range_high, 
                  int(random.normalvariate(base_age, 15))))
        
        person = PersonData(
            age=age,
            gender=gender_choices[i],
            income=random.uniform(income_low, income_high),
            location=location_choices[i]
        )
        data.append(person)
    
    return data


def map_categorical_to_color_value(category: str, categories: List[str]) -> int:
    """
    Map categorical values to color values 0-255.
    
    Args:
        category: The category value
        categories: List of all possible categories
        
    Returns:
        Color value from 0-255 distributed proportionally
    """
    if category not in categories:
        return 128  # Default middle value
    
    index = categories.index(category)
    num_categories = len(categories)
    
    if num_categories == 1:
        return 128
    elif num_categories == 2:
        return [0, 255][index]
    elif num_categories == 3:
        return [0, 128, 255][index]
    else:
        # For more categories, distribute evenly across 0-255
        return int(index * 255 / (num_categories - 1))


class VisualAnalyzer:
    """Real-time visual analyzer for Distilled processor output."""
    
    def __init__(self, processor: DistilledProcessor, grading_functions: Dict[str, Any]):
        self.processor = processor
        self.grading_functions = grading_functions
        
        # Data storage for plotting
        self.sent_points = deque(maxlen=2000)  # Keep last 2000 sent points
        self.timestamps = deque(maxlen=2000)
        
        # Batch averages for time series
        self.batch_averages = deque(maxlen=500)  # Keep last 500 batch averages
        self.batch_timestamps = deque(maxlen=500)
        
        # Rolling averages for current trend (all sent points over time)
        self.rolling_averages = deque(maxlen=500)  # Keep last 500 rolling averages
        self.rolling_timestamps = deque(maxlen=500)
        
        # Expected/target values over time
        self.expected_values = deque(maxlen=500)  # Keep last 500 expected values
        self.expected_timestamps = deque(maxlen=500)
        
        # Set up the plot with 2 subplots
        self.fig, self.axes = plt.subplots(1, 2, figsize=(16, 8))
        self.fig.suptitle('Distilled Processor - Real-Time Sent Data Visualization', fontsize=16)
        
        # Configure subplots
        self.setup_plots()
        
        # Animation
        self.ani = None
        
    def setup_plots(self):
        """Configure the subplot layout and styling."""
        
        # Main scatter plot: Age (X) vs Income (Y), colored by Gender (Yellow) and Location (Blue)
        self.axes[0].set_title('Age vs Income - All Sent Points\n(Yellow=Gender: Dark→Light = Male→Female, Blue=Location: Dark→Light = Urban→Rural)')
        self.axes[0].set_xlabel('Age (years)')
        self.axes[0].set_ylabel('Income ($)')
        self.axes[0].grid(True, alpha=0.3)
        
        # Time series of batch averages
        self.axes[1].set_title('Multi-Dimensional Time Series with Fading Trails\n(Current Average | Batch Average | Expected Target)')
        self.axes[1].set_xlabel('Time (seconds)')
        self.axes[1].set_ylabel('Age vs Income (scaled)')
        self.axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
    def process_batch_and_update(self, batch_data: List[PersonData]):
        """Process a batch and update visualization data."""
        
        # Process through Distilled
        selected_points = self.processor.process_batch(batch_data)
        current_time = time.time()
        
        # Extract data from selected points
        for point in selected_points:
            if point.vector_values:
                self.sent_points.append(point.vector_values)
                self.timestamps.append(current_time)
        
        # Calculate batch averages if we have points
        if selected_points:
            ages = []
            incomes = []
            genders = []
            locations = []
            
            for point in selected_points:
                if point.vector_values:
                    ages.append(point.vector_values.get('age', 0))
                    incomes.append(point.vector_values.get('income', 0))
                    genders.append(point.vector_values.get('gender', 'male'))
                    locations.append(point.vector_values.get('location', 'urban'))
            
            if ages:
                # Calculate averages
                avg_age = sum(ages) / len(ages)
                avg_income = sum(incomes) / len(incomes)
                
                # Calculate gender percentages
                gender_counts = {'male': 0, 'female': 0}
                for gender in genders:
                    if gender in gender_counts:
                        gender_counts[gender] += 1
                
                gender_avg = 0  # Weighted average: male=0, female=128
                total_points = len(genders)
                if total_points > 0:
                    gender_avg = (gender_counts['female'] * 128) / total_points
                
                # Calculate location percentages
                location_counts = {'urban': 0, 'suburban': 0, 'rural': 0}
                for location in locations:
                    if location in location_counts:
                        location_counts[location] += 1
                
                location_avg = 0  # Weighted average: urban=0, suburban=128, rural=255
                if total_points > 0:
                    location_avg = (location_counts['suburban'] * 128 + location_counts['rural'] * 255) / total_points
                
                # Store batch averages
                self.batch_averages.append({
                    'age': avg_age,
                    'income': avg_income,
                    'gender': gender_avg,
                    'location': location_avg
                })
                self.batch_timestamps.append(current_time)
        
        # Calculate rolling average from all sent points (not just current batch)
        if self.sent_points:
            all_ages = []
            all_incomes = []
            all_genders = []
            all_locations = []
            
            for point_data in self.sent_points:
                if all(key in point_data for key in ['age', 'income', 'gender', 'location']):
                    all_ages.append(point_data['age'])
                    all_incomes.append(point_data['income'])
                    all_genders.append(point_data['gender'])
                    all_locations.append(point_data['location'])
            
            if all_ages:
                # Calculate rolling averages
                rolling_age = sum(all_ages) / len(all_ages)
                rolling_income = sum(all_incomes) / len(all_incomes)
                
                # Calculate gender/location proportions for rolling average
                gender_counts = {'male': 0, 'female': 0}
                for gender in all_genders:
                    if gender in gender_counts:
                        gender_counts[gender] += 1
                
                rolling_gender = 0
                total_points = len(all_genders)
                if total_points > 0:
                    rolling_gender = (gender_counts['female'] * 255) / total_points  # 0-255 scale
                
                location_counts = {'urban': 0, 'suburban': 0, 'rural': 0}
                for location in all_locations:
                    if location in location_counts:
                        location_counts[location] += 1
                
                rolling_location = 0
                if total_points > 0:
                    rolling_location = (location_counts['suburban'] * 128 + location_counts['rural'] * 255) / total_points
                
                # Store rolling averages
                self.rolling_averages.append({
                    'age': rolling_age,
                    'income': rolling_income,
                    'gender': rolling_gender,
                    'location': rolling_location
                })
                self.rolling_timestamps.append(current_time)
        
        # Calculate expected/target values based on current time
        target_age = 45 + 12 * math.sin(current_time * 2 * math.pi / 540)
        target_income = 85000 + 30000 * math.cos(current_time * 2 * math.pi / 660 + math.pi/6)
        
        # Calculate expected gender ratio (male_pct from generate_sample_data)
        male_pct = max(0.2, min(0.8, 0.5 + 0.2 * math.sin(current_time * 2 * math.pi / 480)))
        female_pct = 1.0 - male_pct
        target_gender = female_pct * 255  # 0-255 scale
        
        # Calculate expected location ratios
        urban_pct = max(0.15, min(0.65, 0.4 + 0.2 * math.cos(current_time * 2 * math.pi / 600)))
        suburban_pct = max(0.15, min(0.45, 0.3 + 0.12 * math.sin(current_time * 2 * math.pi / 420 + math.pi/4)))  
        rural_pct = max(0.1, min(0.55, 0.3 + 0.18 * math.sin(current_time * 2 * math.pi / 900 + math.pi/2)))
        
        # Normalize location percentages
        total_location = urban_pct + suburban_pct + rural_pct
        urban_pct /= total_location
        suburban_pct /= total_location
        rural_pct /= total_location
        
        target_location = suburban_pct * 128 + rural_pct * 255
        
        # Store expected values
        self.expected_values.append({
            'age': target_age,
            'income': target_income,
            'gender': target_gender,
            'location': target_location
        })
        self.expected_timestamps.append(current_time)
        
        return selected_points
    
    def update_plots(self, frame):
        """Update all plots with current data."""
        
        if not self.sent_points:
            return
        
        # Clear all axes
        for ax in self.axes:
            ax.clear()
        
        # Re-setup plots
        self.setup_plots()
        
        # ===== LEFT PLOT: Age vs Income scatter with color-coded dimensions =====
        
        # Extract data from sent points
        ages = []
        incomes = []
        genders = []
        locations = []
        
        gender_categories = ['male', 'female']
        location_categories = ['urban', 'suburban', 'rural']
        
        for point_data in self.sent_points:
            if all(key in point_data for key in ['age', 'income', 'gender', 'location']):
                ages.append(point_data['age'])
                incomes.append(point_data['income'])
                genders.append(point_data['gender'])
                locations.append(point_data['location'])
        
        if ages:
            # Create colors: Yellow channel (gender) + Blue channel (location)
            colors = []
            
            for gender, location in zip(genders, locations):
                # Map gender to green intensity (affects Green channel)
                gender_value = map_categorical_to_color_value(gender, gender_categories) / 255.0
                
                # Map location to blue intensity (affects Blue channel)
                location_value = map_categorical_to_color_value(location, location_categories) / 255.0
                
                # Create RGB color: Red=base, Green=gender, Blue=location
                red = 1  # Base red at 128 (0.5) for visibility
                green = gender_value  # Green channel for gender (third dimension)
                blue = location_value  # Blue channel for location (fourth dimension)
                
                colors.append((red, green, blue))
            
            # Plot the scatter
            scatter = self.axes[0].scatter(ages, incomes, c=colors, alpha=0.7, s=30, edgecolors='black', linewidth=0.5)
            
            # Add color legend information
            legend_text = (
                "Color Guide:\n"
                "Green Intensity (Gender): Red→Yellow = Male→Female\n"
                "Blue Intensity (Location): No Blue→Full Blue = Urban→Rural\n"
                "Examples: Red=Male+Urban, Yellow=Female+Urban\n"
                "          Purple=Male+Rural, Pink=Female+Rural"
            )
            self.axes[0].text(0.02, 0.98, legend_text, transform=self.axes[0].transAxes, 
                            verticalalignment='top', fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # ===== RIGHT PLOT: Multi-dimensional time series with fading trails =====
        
        if len(self.rolling_timestamps) > 1:
            # Get current time for calculating fade
            current_time = time.time()
            start_time = self.rolling_timestamps[0]
            
            # Helper function to create RGB color from average values
            def create_color_from_averages(age, income, gender_val, location_val):
                # Normalize age and income to 0-1 range for positioning
                age_norm = (age - 18) / (85 - 18)  # Age range 18-85
                income_norm = (income - 25000) / (150000 - 25000)  # Income range 25k-150k
                
                # Gender and location already on 0-255 scale, convert to 0-1
                gender_norm = gender_val / 255.0
                location_norm = location_val / 255.0
                
                # Create RGB: Red=base, Green=gender, Blue=location
                red = 0.5
                green = gender_norm
                blue = location_norm
                
                return (red, green, blue), age_norm, income_norm
            
            # Plot each time series with fading trails
            time_window = 120  # Show last 2 minutes of data
            
            # Store current/most recent points to draw last (on top)
            current_points = []
            
            # 1. TRAIL POINTS: Current/Rolling Average (all except most recent)
            if len(self.rolling_averages) > 1:
                times = np.array(self.rolling_timestamps)
                recent_mask = times >= (current_time - time_window)
                recent_times = times[recent_mask]
                recent_averages = [self.rolling_averages[i] for i in range(len(self.rolling_averages)) if recent_mask[i]]
                
                if len(recent_times) > 0:
                    for i, (t, avg) in enumerate(zip(recent_times, recent_averages)):
                        is_most_recent = i == len(recent_times) - 1
                        
                        if not is_most_recent:  # Draw trail points first
                            color, x_pos, y_pos = create_color_from_averages(
                                avg['age'], avg['income'], avg['gender'], avg['location']
                            )
                            
                            # Calculate fade and size based on age of point
                            age_ratio = (current_time - recent_times[i]) / time_window
                            alpha = max(0.1, min(1.0, 1.0 - age_ratio))  # Clamp between 0.1 and 1.0
                            size = max(20, 60 * (1.0 - age_ratio))  # Shrink from 60 to 20
                            
                            # Plot trail point with no edge
                            self.axes[1].scatter(avg['age'], avg['income'] / 1000, 
                                               c=[color], alpha=alpha, s=size, marker='o', 
                                               edgecolors='none', linewidth=0, label='Rolling Avg' if i == 0 else "")
                        else:
                            # Store current point to draw later
                            color, x_pos, y_pos = create_color_from_averages(
                                avg['age'], avg['income'], avg['gender'], avg['location']
                            )
                            current_points.append(('rolling', avg, color))
            
            # 2. TRAIL POINTS: Batch Average (all except most recent)
            if len(self.batch_averages) > 1:
                times = np.array(self.batch_timestamps)
                recent_mask = times >= (current_time - time_window)
                recent_times = times[recent_mask]
                recent_batches = [self.batch_averages[i] for i in range(len(self.batch_averages)) if recent_mask[i]]
                
                if len(recent_times) > 0:
                    for i, (t, batch) in enumerate(zip(recent_times, recent_batches)):
                        is_most_recent = i == len(recent_times) - 1
                        
                        if not is_most_recent:  # Draw trail points first
                            color, x_pos, y_pos = create_color_from_averages(
                                batch['age'], batch['income'], batch['gender'], batch['location']
                            )
                            
                            # Calculate fade and size based on age of point
                            age_ratio = (current_time - recent_times[i]) / time_window
                            alpha = max(0.1, min(1.0, 1.0 - age_ratio))  # Clamp between 0.1 and 1.0
                            size = max(15, 40 * (1.0 - age_ratio))  # Shrink from 40 to 15
                            
                            # Plot trail point with no edge
                            self.axes[1].scatter(batch['age'], batch['income'] / 1000, 
                                               c=[color], alpha=alpha, s=size, marker='^', 
                                               edgecolors='none', linewidth=0, label='Batch Avg' if i == 0 else "")
                        else:
                            # Store current point to draw later
                            color, x_pos, y_pos = create_color_from_averages(
                                batch['age'], batch['income'], batch['gender'], batch['location']
                            )
                            current_points.append(('batch', batch, color))
            
            # 3. TRAIL POINTS: Expected/Target values (all except most recent)
            if len(self.expected_values) > 1:
                times = np.array(self.expected_timestamps)
                recent_mask = times >= (current_time - time_window)
                recent_times = times[recent_mask]
                recent_expected = [self.expected_values[i] for i in range(len(self.expected_values)) if recent_mask[i]]
                
                if len(recent_times) > 0:
                    for i, (t, expected) in enumerate(zip(recent_times, recent_expected)):
                        is_most_recent = i == len(recent_times) - 1
                        
                        if not is_most_recent:  # Draw trail points first
                            color, x_pos, y_pos = create_color_from_averages(
                                expected['age'], expected['income'], expected['gender'], expected['location']
                            )
                            
                            # Calculate fade and size based on age of point
                            age_ratio = (current_time - recent_times[i]) / time_window
                            alpha = max(0.1, min(1.0, 1.0 - age_ratio))  # Clamp between 0.1 and 1.0
                            size = max(10, 30 * (1.0 - age_ratio))  # Shrink from 30 to 10
                            
                            # Plot trail point with no edge
                            self.axes[1].scatter(expected['age'], expected['income'] / 1000, 
                                               c=[color], alpha=alpha, s=size, marker='s', 
                                               edgecolors='none', linewidth=0, label='Expected' if i == 0 else "")
                        else:
                            # Store current point to draw later
                            color, x_pos, y_pos = create_color_from_averages(
                                expected['age'], expected['income'], expected['gender'], expected['location']
                            )
                            current_points.append(('expected', expected, color))
            
            # 4. CURRENT POINTS: Draw all current points on top with edges
            for point_type, data, color in current_points:
                if point_type == 'rolling':
                    self.axes[1].scatter(data['age'], data['income'] / 1000, 
                                       c=[color], alpha=1.0, s=60, marker='o', 
                                       edgecolors='black', linewidth=0.5)
                elif point_type == 'batch':
                    self.axes[1].scatter(data['age'], data['income'] / 1000, 
                                       c=[color], alpha=1.0, s=40, marker='^', 
                                       edgecolors='black', linewidth=0.5)
                elif point_type == 'expected':
                    self.axes[1].scatter(data['age'], data['income'] / 1000, 
                                       c=[color], alpha=1.0, s=30, marker='s', 
                                       edgecolors='white', linewidth=1)
            
            # Add legend and explanation
            self.axes[1].legend(loc='upper right', fontsize=9)
            
            # Add explanation
            explanation = (
                "Each point uses same RGB color as left panel:\n"
                "Red=Base, Green=Gender(Male→Female), Blue=Location(Urban→Rural)\n"
                "Circles=Rolling Avg, Triangles=Batch Avg, Squares=Expected\n"
                "Older points fade & shrink over time (2min window)"
            )
            self.axes[1].text(0.02, 0.02, explanation, transform=self.axes[1].transAxes, 
                            fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        plt.tight_layout()
    
    def start_animation(self, interval=1000):
        """Start the real-time animation."""
        self.ani = animation.FuncAnimation(self.fig, self.update_plots, interval=interval, blit=False)
        return self.ani


def main():
    """Main visual analysis example."""
    print("Distilled Visual Analysis Example")
    print("=" * 50)
    print("🎨 REAL-TIME VISUALIZATION - Color-coded multi-dimensional view!")
    print("Left: Age vs Income scatter (Yellow=Gender, Blue=Location)")
    print("Right: Batch averages over time with targets")
    print("=" * 50)
    
    # Create grading functions
    grading_functions = create_sample_grading_functions()
    print(f"Created {len(grading_functions)} grading functions")
    
    # Initialize processor
    processor = DistilledProcessor(
        grading_functions=grading_functions,
        time_horizon_seconds=60,  # 1 minute window
        reduction_percentage=0.1,  # 10% pass-through
        batch_size=100
    )
    print(f"Initialized processor with 1-minute time horizon and 10% reduction")
    
    # Create visual analyzer
    analyzer = VisualAnalyzer(processor, grading_functions)
    print("Setting up real-time visualization...")
    
    # Function to generate and process data continuously
    def data_generator():
        batch_num = 0
        while True:
            batch_num += 1
            
            # Generate and process batch
            batch_data = generate_sample_data(100, batch_num)
            selected_points = analyzer.process_batch_and_update(batch_data)
            
            print(f"Batch {batch_num}: {len(batch_data)} → {len(selected_points)} points")
            
            # Small delay to control update rate
            time.sleep(0.1)
    
    # Start data generation in a separate thread
    import threading
    data_thread = threading.Thread(target=data_generator, daemon=True)
    data_thread.start()
    
    # Start animation
    print("Starting real-time visualization...")
    print("Note: Requires matplotlib - install with: pip install matplotlib")
    print("Close the plot window to stop.")
    
    ani = analyzer.start_animation(interval=500)  # Update every 500ms
    plt.show()


if __name__ == "__main__":
    main() 