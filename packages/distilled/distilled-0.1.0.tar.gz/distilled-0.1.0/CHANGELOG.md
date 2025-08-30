# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation for PyPI

## [0.1.0] - 2024-01-XX

### Added
- Initial implementation of DistilledProcessor for data stream reduction
- DataPoint class for representing individual data points
- Grading functions: NumericGrader, CategoricalGrader
- Vector analysis and proportion calculation capabilities
- Time horizon management with sliding window
- Generator/coroutine pattern for efficient streaming
- Configurable reduction percentage and batch processing
- Comprehensive documentation and examples
- MIT License
- Basic test structure

### Architecture
- Object-oriented design with extensible grading functions
- Spatial vector analysis for optimal data point selection
- A/B testing strategies for proportional representation
- FIFO queues with automatic cleanup for time horizon management

### Features
- Proportional representation maintenance across time windows
- Real-time processing optimization for high-throughput streams
- Configurable time horizons (60-3600 seconds)
- Extensible grading function system
- Statistical accuracy preservation in multivariate data

[Unreleased]: https://github.com/yourusername/distilled/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/distilled/releases/tag/v0.1.0
