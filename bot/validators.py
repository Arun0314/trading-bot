VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_order_inputs(symbol, side, order_type, quantity, price=None):
    """Raises ValueError with a human-readable message on bad input."""

    if not symbol or not symbol.strip():
        raise ValueError("Symbol can't be empty (e.g. BTCUSDT)")

    if side not in VALID_SIDES:
        raise ValueError(f"Side must be BUY or SELL, got: '{side}'")

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be MARKET or LIMIT, got: '{order_type}'")

    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got: {quantity}")

    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("LIMIT orders require a valid --price (> 0)")
