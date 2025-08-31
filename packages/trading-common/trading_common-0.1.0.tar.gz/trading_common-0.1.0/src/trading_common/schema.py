from trading_contracts.loader import validate_event


def ensure(name: str, payload: dict) -> dict:
    """
    Validate event payload against schema and return the payload if valid.

    Args:
        name: Event name in format 'service.event_type@vN' (e.g., 'md.candle.closed@v1')
        payload: Event payload to validate

    Returns:
        The validated payload

    Raises:
        ValidationError: If payload doesn't match schema
    """
    validate_event(name, payload)
    return payload
