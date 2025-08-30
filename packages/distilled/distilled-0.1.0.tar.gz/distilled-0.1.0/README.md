# Distilled

A data stream reduction middleware that intelligently reduces large multivariate data streams to representative subsets while maintaining proportional characteristics.

## Overview

Distilled uses spatial vector analysis and A/B testing strategies to continuously analyze streaming data and pass along a configurable percentage (default 10%) that accurately represents the full dataset's characteristics across a sliding time window.

### Key Features

- **Proportional Representation**: Maintains statistical accuracy of multivariate characteristics
- **Sliding Time Window**: Configurable time horizon (60-3600 seconds) for analysis
- **Extensible Design**: Object-oriented architecture with customizable grading functions
- **Generator/Coroutine Pattern**: Efficient streaming data processing
- **Real-time Processing**: Optimized for high-throughput data streams

## How It Works

1. **Data Ingestion**: Receives batches of raw data points
2. **Vector Evaluation**: Applies grading functions to extract characteristics
3. **Proportion Analysis**: Calculates current vs. sent data proportions
4. **Optimal Selection**: Uses vector analysis to select representative subset
5. **Time Horizon Management**: Maintains FIFO queues with automatic cleanup

## Architecture

```
Raw Data Stream → Grading Functions → Vector Analysis → Optimal Selection → Reduced Stream
                     ↓                    ↓               ↓
                 DataPoints         Proportions      Time Horizon
                                   Comparison        Management
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from distilled import DistilledProcessor, NumericGrader, CategoricalGrader

# Define how to evaluate your data characteristics
grading_functions = {
    "age": NumericGrader("age", lambda person: float(person.age)),
    "gender": CategoricalGrader("gender", ["male", "female", "other"], 
                               lambda person: person.gender.lower()),
    "income": NumericGrader("income", lambda person: person.income)
}

# Create processor
processor = DistilledProcessor(
    grading_functions=grading_functions,
    time_horizon_seconds=3600,  # 1 hour window
    reduction_percentage=0.1,   # 10% pass-through
    batch_size=100
)

# Process data batches
batch_data = get_your_data_batch()  # Your data source
selected_points = processor.process_batch(batch_data)

# selected_points now contains ~10% of input that best represents full dataset
```

## Core Classes

### DistilledProcessor

Main processor class implementing the generator/coroutine pattern:

- **process_batch()**: Process a batch and return selected subset
- **get_current_stats()**: Get current proportion statistics
- **reset()**: Reset processor state

### DataPoint

Represents individual data points with metadata:

- `data`: Raw data payload
- `timestamp`: Processing timestamp  
- `vector_values`: Evaluated characteristics
- `sent_previously`: Tracking flag

### Grading Functions

Define how to evaluate data characteristics:

- **NumericGrader**: Extracts numerical values
- **CategoricalGrader**: Classifies into predefined categories
- **LambdaGrader**: Quick wrapper for simple functions

## Selection Algorithm

The core algorithm works as follows:

1. **Gap Analysis**: Calculate representation gaps between current and sent data
2. **Point Scoring**: Score each candidate point's improvement potential
3. **Greedy Selection**: Select points that best minimize representation gaps
4. **Tie Breaking**: Prioritize smallest proportional buckets first
5. **Update Tracking**: Maintain sent data proportions for next iteration

## Configuration

### Time Horizon

Controls how long data is retained for analysis:

```python
processor = DistilledProcessor(
    grading_functions=functions,
    time_horizon_seconds=1800  # 30 minutes
)
```

### Reduction Percentage

Controls what percentage of data passes through:

```python
processor = DistilledProcessor(
    grading_functions=functions,
    reduction_percentage=0.05  # 5% pass-through
)
```

### Batch Size

Controls internal processing batch size:

```python
processor = DistilledProcessor(
    grading_functions=functions,
    batch_size=50  # Smaller batches
)
```

## Examples

See `examples/basic_usage.py` for a complete working example with sample data.

## Testing

Run tests with:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_basic.py
```

## Development Status

**Current Status**: Architecture and API design complete with method stubs.

**Next Steps**:
1. Implement grading function evaluation
2. Implement proportion calculation algorithms  
3. Implement vector analysis and selection logic
4. Implement time horizon management 
5. Add comprehensive testing
6. Performance optimization

## Contributing

This is an open source project. Contributions are welcome! 

## License

MIT License - see LICENSE file for details.

---

*Distilled - Intelligent data stream reduction for the modern data pipeline.* 