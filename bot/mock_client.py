"""
Mock Binance client for demo/offline mode.
Simulates realistic order responses without needing API keys.
"""
import random
import time
import uuid
from bot.logging_config import setup_logger

logger = setup_logger()

# Simulated market prices (approximate)
MOCK_PRICES = {
    "BTCUSDT": 67432.50,
    "ETHUSDT": 3215.80,
    "SOLUSDT": 148.65,
    "BNBUSDT": 598.20,
    "XRPUSDT": 0.5234,
    "DOGEUSDT": 0.1567,
    "ADAUSDT": 0.4521,
    "AVAXUSDT": 35.72,
    "DOTUSDT": 7.15,
    "MATICUSDT": 0.7823,
    "LINKUSDT": 14.56,
    "LTCUSDT": 84.30,
}

DEFAULT_PRICE = 100.00


class MockFuturesClient:
    """Drop-in replacement for binance.client.Client in demo mode."""

    def __init__(self):
        logger.debug("MockFuturesClient initialized (demo mode — no real API calls)")

    def futures_create_order(self, **params):
        """Simulate a futures order placement with realistic response data."""
        symbol = params.get("symbol", "UNKNOWN")
        side = params.get("side", "BUY")
        order_type = params.get("type", "MARKET")
        quantity = params.get("quantity", 0)
        price = params.get("price")

        # Look up a simulated market price
        base_price = MOCK_PRICES.get(symbol, DEFAULT_PRICE)

        # Add slight random slippage for realism (±0.05 %)
        slippage = random.uniform(-0.0005, 0.0005)
        fill_price = round(base_price * (1 + slippage), 4)

        if order_type == "LIMIT" and price is not None:
            fill_price = float(price)

        order_id = random.randint(1_000_000_000, 9_999_999_999)
        client_order_id = f"x-demo-{uuid.uuid4().hex[:12]}"
        timestamp = int(time.time() * 1000)

        status = "FILLED" if order_type == "MARKET" else "NEW"

        response = {
            "orderId": order_id,
            "symbol": symbol,
            "status": status,
            "clientOrderId": client_order_id,
            "price": str(fill_price) if order_type == "LIMIT" else "0",
            "avgPrice": str(fill_price),
            "origQty": str(quantity),
            "executedQty": str(quantity) if order_type == "MARKET" else "0",
            "cumQuote": str(round(fill_price * float(quantity), 4)),
            "timeInForce": params.get("timeInForce", "GTC"),
            "type": order_type,
            "side": side,
            "updateTime": timestamp,
            "workingType": "CONTRACT_PRICE",
            "fills": [
                {
                    "price": str(fill_price),
                    "qty": str(quantity),
                    "commission": str(round(fill_price * float(quantity) * 0.0004, 6)),
                    "commissionAsset": "USDT",
                }
            ] if order_type == "MARKET" else [],
        }

        logger.info(f"[DEMO] Simulated order response: {response}")
        return response


def get_demo_client():
    """Return a mock client for demo/offline use."""
    logger.info("Starting in DEMO mode — orders are simulated, nothing is sent to Binance")
    return MockFuturesClient()
