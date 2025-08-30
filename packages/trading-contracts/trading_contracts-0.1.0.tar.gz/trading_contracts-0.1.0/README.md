# Trading Contracts

JSON Schema validation library for trading platform events. This package provides schemas and validation tools for Kafka events used across the trading platform services.

## Features

- **JSON Schema Validation**: Pre-defined schemas for all trading platform events
- **Python Package**: Easy integration with Python services
- **Version Management**: Schema versioning with semantic versioning support
- **Type Safety**: Full type hints and validation

## Installation

```bash
pip install trading-contracts
```

## Quick Start

```python
from trading_contracts import validate_event, load_schema

# Validate an event
event_data = {
    "event_id": "evt_123",
    "version": 1,
    "instance_id": "inst_001",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "price": "45000.50",
    "ts": "2024-01-15T10:30:00Z"
}

try:
    validate_event("strategy.signal@v1", event_data)
    print("Event is valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")

# Load schema for inspection
schema = load_schema("strategy.signal@v1")
print(f"Schema title: {schema['title']}")
```

## Available Schemas

| Event | Schema File | Description |
|-------|-------------|-------------|
| `strategy.signal@v1` | `strategy.signal.v1.schema.json` | Trading signals from strategy service |
| `exec.order.filled@v1` | `exec.order.filled.v1.schema.json` | Order execution confirmations |
| `risk.signal.allowed@v1` | `risk.signal.allowed.v1.schema.json` | Risk validation results |
| `pf.pnl.updated@v1` | `pf.pnl.updated.v1.schema.json` | Portfolio P&L updates |
| `runs.started@v1` | `runs.started.v1.schema.json` | Strategy run lifecycle events |

## Schema Naming Convention

Schemas follow the pattern: `{service}.{event_type}@v{version}`

- **service**: Service identifier (strategy, exec, risk, pf, runs)
- **event_type**: Specific event type (signal, order.filled, etc.)
- **version**: Schema version number

## Development

### Setup

```bash
git clone <repository>
cd contracts
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black src/
isort src/
mypy src/
```

## Adding New Schemas

1. Create schema file in `kafka/` directory
2. Follow naming convention: `{event}.v{version}.schema.json`
3. Add example in `examples/` directory
4. Update this README with new event details

## Schema Requirements

All schemas must include:
- `event_id`: Unique event identifier
- `version`: Schema version (const value)
- `ts`: Timestamp in ISO 8601 format
- `additionalProperties: false` for strict validation

## License

MIT License - see LICENSE file for details.
