# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial schema definitions for core trading events
- Python package with validation utilities
- Support for strategy signals, order execution, risk validation, portfolio P&L, and run lifecycle events

## [0.1.0] - 2024-01-15

### Added
- `strategy.signal@v1` schema for trading strategy signals
- `exec.order.filled@v1` schema for order execution confirmations
- `risk.signal.allowed@v1` schema for risk validation results
- `pf.pnl.updated@v1` schema for portfolio P&L updates
- `runs.started@v1` schema for strategy run lifecycle events
- Python package `trading-contracts` with validation utilities
- Comprehensive examples for all event types
- Documentation and development setup

### Technical Details
- JSON Schema Draft 2020-12 compliance
- Strict validation with `additionalProperties: false`
- ISO 8601 timestamp format requirements
- Semantic versioning for all schemas
- Type-safe Python API with full type hints
