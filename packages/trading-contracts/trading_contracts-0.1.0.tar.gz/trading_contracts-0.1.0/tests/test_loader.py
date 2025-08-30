"""
Tests for trading_contracts.loader module
"""

import pytest
from trading_contracts.loader import load_schema, validate_event, get_schema_names


class TestLoadSchema:
    """Test schema loading functionality"""
    
    def test_load_strategy_signal_schema(self):
        """Test loading strategy.signal@v1 schema"""
        schema = load_schema("strategy.signal@v1")
        
        assert schema["$id"] == "kafka/strategy.signal.v1.schema.json"
        assert schema["title"] == "strategy.signal@v1"
        assert schema["type"] == "object"
        assert "event_id" in schema["required"]
        assert "version" in schema["required"]
        
    def test_load_exec_order_filled_schema(self):
        """Test loading exec.order.filled@v1 schema"""
        schema = load_schema("exec.order.filled@v1")
        
        assert schema["$id"] == "kafka/exec.order.filled.v1.schema.json"
        assert schema["title"] == "exec.order.filled@v1"
        assert "account_id" in schema["required"]
        
    def test_load_nonexistent_schema(self):
        """Test loading non-existent schema raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_schema("nonexistent.event@v1")


class TestValidateEvent:
    """Test event validation functionality"""
    
    def test_validate_valid_strategy_signal(self):
        """Test validation of valid strategy signal event"""
        event_data = {
            "event_id": "evt_123",
            "version": 1,
            "instance_id": "inst_001",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": "45000.50",
            "ts": "2024-01-15T10:30:00Z"
        }
        
        # Should not raise any exception
        validate_event("strategy.signal@v1", event_data)
        
    def test_validate_invalid_strategy_signal(self):
        """Test validation of invalid strategy signal event"""
        event_data = {
            "event_id": "evt_123",
            "version": 1,
            "instance_id": "inst_001",
            "symbol": "BTCUSDT",
            "side": "INVALID_SIDE",  # Invalid enum value
            "price": "45000.50",
            "ts": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(Exception):  # ValidationError or similar
            validate_event("strategy.signal@v1", event_data)
            
    def test_validate_missing_required_fields(self):
        """Test validation fails when required fields are missing"""
        event_data = {
            "event_id": "evt_123",
            "version": 1,
            # Missing required fields: instance_id, symbol, side, price, ts
        }
        
        with pytest.raises(Exception):
            validate_event("strategy.signal@v1", event_data)
            
    def test_validate_exec_order_filled(self):
        """Test validation of exec.order.filled event"""
        event_data = {
            "event_id": "evt_fill_123",
            "version": 1,
            "account_id": "acc_001",
            "order_id": "ord_123",
            "fill_id": "fill_123",
            "instrument_key": "BTCUSDT",
            "price": "45000.50",
            "qty": "0.1",
            "ts": "2024-01-15T10:31:00Z"
        }
        
        # Should not raise any exception
        validate_event("exec.order.filled@v1", event_data)


class TestGetSchemaNames:
    """Test schema discovery functionality"""
    
    def test_get_schema_names(self):
        """Test getting list of available schema names"""
        names = get_schema_names()
        
        assert isinstance(names, list)
        assert "strategy.signal@v1" in names
        assert "exec.order.filled@v1" in names
        assert "risk.signal.allowed@v1" in names
        assert "pf.pnl.updated@v1" in names
        assert "runs.started@v1" in names
        
        # Check format: should be sorted and follow pattern
        for name in names:
            assert "@v" in name
            assert name.count("@") == 1
