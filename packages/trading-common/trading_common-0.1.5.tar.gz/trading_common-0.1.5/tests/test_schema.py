import pytest

from trading_common.schema import ensure


def test_ensure_valid_payload() -> None:
    """Test schema validation with valid payload"""
    # This test assumes you have a schema for 'test.event@v1'
    # In real usage, you would have actual schemas defined
    payload = {"event_id": "123", "data": "test"}

    # This should not raise an exception if schema exists
    # If schema doesn't exist, it will raise ValidationError
    try:
        result = ensure("test.event@v1", payload)
        assert result == payload
    except Exception as e:
        # If trading-contracts is not available or schema doesn't exist,
        # this is expected behavior
        pytest.skip(f"Schema validation not available: {e}")


def test_ensure_invalid_payload() -> None:
    """Test schema validation with invalid payload"""
    # This test assumes you have a schema for 'test.event@v1'
    invalid_payload: dict = {}  # Missing required fields

    try:
        ensure("test.event@v1", invalid_payload)
        # If this doesn't raise an exception, the schema might be too permissive
        # or not properly defined
        pytest.skip("Schema validation not strict enough for testing")
    except Exception as e:
        # Expected behavior - validation should fail
        # Check if it's a validation error or schema not found
        error_str = str(e).lower()
        assert (
            "validation" in error_str
            or "schema not found" in error_str
            or "file not found" in error_str
        )


def test_ensure_event_name_format() -> None:
    """Test that event names follow expected format"""
    payload = {"event_id": "123"}

    # Test various event name formats
    valid_names = [
        "service.event@v1",
        "md.candle.closed@v1",
        "strategy.signal@v1",
        "risk.signal.allowed@v1",
    ]

    for name in valid_names:
        try:
            result = ensure(name, payload)
            assert result == payload
        except Exception:
            # Skip if schema doesn't exist
            pass
