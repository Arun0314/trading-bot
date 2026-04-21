from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.logging_config import setup_logger

logger = setup_logger()


def place_order(client, symbol, side, order_type, quantity, price=None):
    """
    Places a futures order and returns a cleaned-up summary dict.
    Raises on API/network errors after logging them.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    logger.info(f"Placing order: {params}")

    try:
        resp = client.futures_create_order(**params)
        logger.info(f"Order response: {resp}")
    except BinanceAPIException as e:
        logger.error(f"Binance API error [{e.status_code}]: {e.message}")
        raise
    except BinanceRequestException as e:
        logger.error(f"Network/request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing order: {e}")
        raise

    return _parse_response(resp)


def _parse_response(resp):
    # Pull out the fields we actually care about
    fills = resp.get("fills", [])
    avg_price = None
    if fills:
        total_qty = sum(float(f["qty"]) for f in fills)
        avg_price = sum(float(f["price"]) * float(f["qty"]) for f in fills) / total_qty

    return {
        "order_id": resp.get("orderId"),
        "symbol": resp.get("symbol"),
        "side": resp.get("side"),
        "type": resp.get("type"),
        "status": resp.get("status"),
        "quantity": resp.get("origQty"),
        "price": resp.get("price") if resp.get("price") != "0" else avg_price,
        "client_order_id": resp.get("clientOrderId"),
    }
