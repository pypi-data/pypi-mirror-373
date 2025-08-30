"""
Basic usage example for Distilled data stream reduction.

This example demonstrates how to set up and use the DistilledProcessor
with sample data containing multiple characteristics.
"""

import sys
import os
# Add the parent directory to Python path so we can import distilled
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distilled import DistilledProcessor, NumericGrader, CategoricalGrader
import random
import time
from typing import Dict, Any


# Sample data structure
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
    """
    Create sample grading functions for person data.
    
    Returns:
        Dictionary of grading functions for different characteristics
    """
    
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
    
    # Categorical grader for gender
    gender_grader = CategoricalGrader(
        name="gender",
        categories=["male", "female", "other"],
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
    """
    Generate sample person data with cyclical oscillating distributions over time.
    
    Args:
        count: Number of sample data points to generate
        batch_num: Current batch number (used for display, actual timing is time-based)
        
    Returns:
        List of PersonData objects with time-varying cyclical characteristics
    """
    import math
    
    # Use actual time for continuous oscillations
    current_time = time.time()
    
    # Gender distribution oscillates with long periods (multiple time horizons)
    # Male: 40% ± 15% with 8-minute period (8 time horizons)
    # Female: 40% ± 15% with 6-minute period (6 time horizons, different phase)
    # Other: 20% ± 8% with 12-minute period (12 time horizons)
    male_pct = max(0.15, min(0.65, 0.4 + 0.15 * math.sin(current_time * 2 * math.pi / 480)))
    female_pct = max(0.15, min(0.65, 0.4 + 0.15 * math.cos(current_time * 2 * math.pi / 360)))
    other_pct = max(0.05, min(0.35, 0.2 + 0.08 * math.sin(current_time * 2 * math.pi / 720 + math.pi/3)))
    
    # Normalize to ensure they sum to 1.0
    total_gender = male_pct + female_pct + other_pct
    male_pct /= total_gender
    female_pct /= total_gender
    other_pct /= total_gender
    
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
        ["male", "female", "other"],
        weights=[male_pct, female_pct, other_pct],
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


def print_current_distribution_targets(batch_num: int):
    """
    Print the current expected oscillating distributions.
    
    Args:
        batch_num: Current batch number (for display only)
    """
    import math
    
    # Use actual time for oscillating targets
    current_time = time.time()
    
    # Calculate current oscillating targets (same formulas as generate_sample_data)
    male_pct = max(0.15, min(0.65, 0.4 + 0.15 * math.sin(current_time * 2 * math.pi / 480)))
    female_pct = max(0.15, min(0.65, 0.4 + 0.15 * math.cos(current_time * 2 * math.pi / 360)))
    other_pct = max(0.05, min(0.35, 0.2 + 0.08 * math.sin(current_time * 2 * math.pi / 720 + math.pi/3)))
    
    # Normalize gender percentages
    total_gender = male_pct + female_pct + other_pct
    male_pct /= total_gender
    female_pct /= total_gender
    other_pct /= total_gender
    
    urban_pct = max(0.15, min(0.65, 0.4 + 0.2 * math.cos(current_time * 2 * math.pi / 600)))
    suburban_pct = max(0.15, min(0.45, 0.3 + 0.12 * math.sin(current_time * 2 * math.pi / 420 + math.pi/4)))  
    rural_pct = max(0.1, min(0.55, 0.3 + 0.18 * math.sin(current_time * 2 * math.pi / 900 + math.pi/2)))
    
    # Normalize location percentages
    total_location = urban_pct + suburban_pct + rural_pct
    urban_pct /= total_location
    suburban_pct /= total_location
    rural_pct /= total_location
    
    base_age = 45 + 12 * math.sin(current_time * 2 * math.pi / 540)
    income_center = 85000 + 30000 * math.cos(current_time * 2 * math.pi / 660 + math.pi/6)
    income_low = max(25000, income_center - 40000)
    income_high = income_center + 40000
    
    print(f"🌊 CURRENT OSCILLATING TARGETS (Batch {batch_num}):")
    print(f"   Gender:   Male {male_pct:.1%}, Female {female_pct:.1%}, Other {other_pct:.1%}")
    print(f"   Location: Urban {urban_pct:.1%}, Suburban {suburban_pct:.1%}, Rural {rural_pct:.1%}")
    print(f"   Age:      Mean ~{base_age:.0f} years (oscillating)")
    print(f"   Income:   ${income_low:,.0f} - ${income_high:,.0f} (center: ${income_center:,.0f})")
    print("-" * 60)


def main():
    """
    Main example demonstrating Distilled usage with continuous processing.
    """
    print("Distilled Data Stream Reduction Example")
    print("=" * 50)
    print("🌊 CONTINUOUS OSCILLATING DISTRIBUTIONS - Real-time sine wave tracking!")
    print("Running at full speed - Press Ctrl+C to stop")
    print("=" * 50)
    
    # Create grading functions
    grading_functions = create_sample_grading_functions()
    print(f"Created {len(grading_functions)} grading functions:")
    for name, grader in grading_functions.items():
        grader_type = "categorical" if grader.is_categorical() else "numeric"
        print(f"  - {name}: {grader_type}")
    
    # Initialize processor
    processor = DistilledProcessor(
        grading_functions=grading_functions,
        time_horizon_seconds=60,  # 1 minute window
        reduction_percentage=0.1,  # 10% pass-through
        batch_size=100
    )
    print(f"\nInitialized processor with 1-minute time horizon and 10% reduction")
    print(f"Processing batches of 100 data points each...\n")
    print("🌊 LONG-TERM OSCILLATING PATTERNS:")
    print("   • Gender: Male 40%±15% (8min), Female 40%±15% (6min), Other 20%±8% (12min)")  
    print("   • Location: Urban 40%±20% (10min), Suburban 30%±12% (7min), Rural 30%±18% (15min)")
    print("   • Age: Mean 45±12 years (9-minute oscillation)")
    print("   • Income: Center $85k±$30k, Range ±$40k (11-minute cycle)")
    print("   Oscillations span multiple time horizons - watch the curve tracking!\n")
    
    # Simulate continuous data stream processing
    batch_num = 0
    total_input = 0
    total_output = 0
    
    try:
        while True:
            batch_num += 1
            
            # Generate batch of sample data with evolving distributions
            batch_data = generate_sample_data(100, batch_num)
            total_input += len(batch_data)
            
            # Process batch through Distilled
            try:
                selected_points = processor.process_batch(batch_data)
                total_output += len(selected_points)
                
                # Get comprehensive statistics
                stats = processor.get_current_stats()
                
                # Clear screen for updated display (optional)
                print("\033[2J\033[H")  # Clear screen and move cursor to top
                
                print("Distilled Data Stream Reduction - Live Statistics")
                print("=" * 60)
                print(f"Batch #{batch_num:,} | Input: {len(batch_data)} → Output: {len(selected_points)} points")
                print(f"Total: {total_input:,} input → {total_output:,} output ({total_output/total_input:.1%} reduction)")
                print(f"Historical window: {stats['historical_data_count']:,} points | Sent: {stats['sent_data_count']:,} points")
                print("=" * 60)
                
                # Display current vs sent proportions for each category
                current_props = stats.get('current_proportions', {})
                sent_props = stats.get('sent_proportions', {})
                
                for var_name in stats.get('grading_function_names', []):
                    print(f"\n📊 {var_name.upper()} DISTRIBUTION:")
                    print("-" * 40)
                    
                    if var_name in current_props and var_name in sent_props:
                        current_data = current_props[var_name]
                        sent_data = sent_props[var_name]
                        
                        # Handle categorical data
                        if current_data.get('type') == 'categorical':
                            print("  Category Breakdown:")
                            categories = current_data.get('categories', {})
                            sent_categories = sent_data.get('categories', {})
                            
                            # Get current oscillating targets for comparison
                            import math
                            current_time = time.time()
                            targets = {}
                            if var_name == 'gender':
                                male_target = max(0.15, min(0.65, 0.4 + 0.15 * math.sin(current_time * 2 * math.pi / 480)))
                                female_target = max(0.15, min(0.65, 0.4 + 0.15 * math.cos(current_time * 2 * math.pi / 360)))
                                other_target = max(0.05, min(0.35, 0.2 + 0.08 * math.sin(current_time * 2 * math.pi / 720 + math.pi/3)))
                                
                                # Calculate targets from time horizon start
                                horizon_start_time = current_time - stats['time_horizon_seconds']
                                male_start = max(0.15, min(0.65, 0.4 + 0.15 * math.sin(horizon_start_time * 2 * math.pi / 480)))
                                female_start = max(0.15, min(0.65, 0.4 + 0.15 * math.cos(horizon_start_time * 2 * math.pi / 360)))
                                other_start = max(0.05, min(0.35, 0.2 + 0.08 * math.sin(horizon_start_time * 2 * math.pi / 720 + math.pi/3)))
                                
                                # Normalize current and start targets
                                total = male_target + female_target + other_target
                                total_start = male_start + female_start + other_start
                                targets = {
                                    'male': male_target / total,
                                    'female': female_target / total,
                                    'other': other_target / total
                                }
                                targets_start = {
                                    'male': male_start / total_start,
                                    'female': female_start / total_start,
                                    'other': other_start / total_start
                                }
                            elif var_name == 'location':
                                urban_target = max(0.15, min(0.65, 0.4 + 0.2 * math.cos(current_time * 2 * math.pi / 600)))
                                suburban_target = max(0.15, min(0.45, 0.3 + 0.12 * math.sin(current_time * 2 * math.pi / 420 + math.pi/4)))  
                                rural_target = max(0.1, min(0.55, 0.3 + 0.18 * math.sin(current_time * 2 * math.pi / 900 + math.pi/2)))
                                
                                # Calculate targets from time horizon start
                                horizon_start_time = current_time - stats['time_horizon_seconds']
                                urban_start = max(0.15, min(0.65, 0.4 + 0.2 * math.cos(horizon_start_time * 2 * math.pi / 600)))
                                suburban_start = max(0.15, min(0.45, 0.3 + 0.12 * math.sin(horizon_start_time * 2 * math.pi / 420 + math.pi/4)))  
                                rural_start = max(0.1, min(0.55, 0.3 + 0.18 * math.sin(horizon_start_time * 2 * math.pi / 900 + math.pi/2)))
                                
                                # Normalize current and start targets
                                total = urban_target + suburban_target + rural_target
                                total_start = urban_start + suburban_start + rural_start
                                targets = {
                                    'urban': urban_target / total,
                                    'suburban': suburban_target / total,
                                    'rural': rural_target / total
                                }
                                targets_start = {
                                    'urban': urban_start / total_start,
                                    'suburban': suburban_start / total_start,
                                    'rural': rural_start / total_start
                                }
                            
                            for category, current_pct in sorted(categories.items()):
                                sent_pct = sent_categories.get(category, 0.0)
                                target_pct = targets.get(category, current_pct)
                                start_target_pct = targets_start.get(category, current_pct) if 'targets_start' in locals() else target_pct
                                
                                # Compare sent vs target instead of sent vs current
                                target_diff = sent_pct - target_pct
                                diff_indicator = "🎯" if abs(target_diff) < 0.03 else ("📈" if target_diff > 0 else "📉")
                                
                                # Show current, sent, target (now), and target (horizon start)
                                print(f"    {category:12}: {current_pct:6.1%} current | {sent_pct:6.1%} sent | {target_pct:6.1%} now | {start_target_pct:6.1%} start {diff_indicator}")
                        
                        # Handle numeric data
                        elif current_data.get('type') == 'numeric':
                            current_mean = current_data.get('average', 0)
                            sent_mean = sent_data.get('average', 0)
                            current_count = current_data.get('total_count', 0)
                            sent_count = sent_data.get('total_count', 0)
                            
                            # Calculate oscillating targets
                            import math
                            current_time = time.time()
                            horizon_start_time = current_time - stats['time_horizon_seconds']
                            
                            if var_name == 'age':
                                target_mean = 45 + 12 * math.sin(current_time * 2 * math.pi / 540)
                                start_target_mean = 45 + 12 * math.sin(horizon_start_time * 2 * math.pi / 540)
                                target_diff = sent_mean - target_mean
                                mean_indicator = "🎯" if abs(target_diff) < 3 else ("📈" if target_diff > 0 else "📉")
                                print(f"  Mean:     {current_mean:8.1f} current | {sent_mean:8.1f} sent | {target_mean:8.1f} now | {start_target_mean:8.1f} start {mean_indicator}")
                            elif var_name == 'income':
                                income_center = 85000 + 30000 * math.cos(current_time * 2 * math.pi / 660 + math.pi/6)
                                start_income_center = 85000 + 30000 * math.cos(horizon_start_time * 2 * math.pi / 660 + math.pi/6)
                                income_low = max(25000, income_center - 40000)
                                income_high = income_center + 40000
                                in_range = income_low <= sent_mean <= income_high
                                mean_indicator = "🎯" if in_range else ("📈" if sent_mean > income_high else "📉")
                                print(f"  Mean:     {current_mean:8.0f} current | {sent_mean:8.0f} sent | {income_center:8.0f} now | {start_income_center:8.0f} start {mean_indicator}")
                                print(f"  Range:    ${income_low:,.0f} - ${income_high:,.0f} (oscillating)")
                            else:
                                mean_diff = sent_mean - current_mean
                                mean_indicator = "✓" if abs(mean_diff) < (abs(current_mean) * 0.1 + 1) else ("↑" if mean_diff > 0 else "↓")
                                print(f"  Mean:     {current_mean:8.1f} current | {sent_mean:8.1f} sent {mean_indicator}")
                            
                            print(f"  Count:    {current_count:8,} current | {sent_count:8,} sent")
                    
                    elif var_name in current_props:
                        print("  (No sent data yet for comparison)")
                        current_data = current_props[var_name]
                        if current_data.get('type') == 'categorical':
                            categories = current_data.get('categories', {})
                            for category, pct in categories.items():
                                print(f"    {category:12}: {pct:6.1%}")
                        elif current_data.get('type') == 'numeric':
                            print(f"  Mean: {current_data.get('average', 0):.1f}")
                            print(f"  Count: {current_data.get('total_count', 0):,}")
                    
                    else:
                        print("  (No data available yet)")
                
                print(f"\n{'='*60}")
                print(f"⏱️  Time Horizon: {stats['time_horizon_seconds']}s | 🎯 Target Reduction: {stats['reduction_percentage']:.0%}")
                
                # Show current distribution targets every 25 batches (since running faster now)
                if batch_num % 25 == 1:
                    print()
                    print_current_distribution_targets(batch_num)
                
                print(f"📈 Press Ctrl+C to stop continuous processing...")
                
            except NotImplementedError:
                print(f"Batch {batch_num}: Implementation not complete yet")
                break
            
            # Small delay to make output readable and see changes over time
            # time.sleep(0.5)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Processing stopped by user")
        print(f"\nFinal Summary:")
        print(f"  Batches processed: {batch_num:,}")
        print(f"  Total input points: {total_input:,}")
        print(f"  Total output points: {total_output:,}")
        if total_input > 0:
            reduction_ratio = total_output / total_input
            print(f"  Final reduction ratio: {reduction_ratio:.2%}")
        
        # Show final statistics
        try:
            final_stats = processor.get_current_stats()
            print(f"\nFinal Processor State:")
            print(f"  Historical data points: {final_stats['historical_data_count']:,}")
            print(f"  Sent data points: {final_stats['sent_data_count']:,}")
        except:
            pass


if __name__ == "__main__":
    main() 