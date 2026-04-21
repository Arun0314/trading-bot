#!/usr/bin/env python3
import argparse
import sys

from bot.validators import validate_order_inputs
from bot.logging_config import setup_logger

logger = setup_logger()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT"
    )
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument(
        "--price", type=float, default=None,
        help="Limit price (required for LIMIT orders)"
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Run in demo mode (simulated orders, no API keys needed)"
    )
    return parser


def print_order_summary(order, demo=False):
    mode_tag = " [DEMO]" if demo else ""
    print(f"\n✓ Order placed successfully{mode_tag}")
    print(f"  Order ID  : {order['order_id']}")
    print(f"  Symbol    : {order['symbol']}")
    print(f"  Side      : {order['side']}")
    print(f"  Type      : {order['type']}")
    print(f"  Quantity  : {order['quantity']}")
    print(f"  Price     : {order['price'] or 'market'}")
    print(f"  Status    : {order['status']}")
    print(f"  Client ID : {order['client_order_id']}\n")


def main():
    parser = build_parser()
    args = parser.parse_args()

    # normalize — people type 'btcusdt' or 'buy' all the time
    symbol = args.symbol.upper().strip()
    side = args.side.upper()
    order_type = args.order_type.upper()

    try:
        validate_order_inputs(symbol, side, order_type, args.quantity, args.price)
    except ValueError as e:
        print(f"✗ Invalid input: {e}", file=sys.stderr)
        sys.exit(1)

    # ---------- client selection ----------
    if args.demo:
        from bot.mock_client import get_demo_client
        client = get_demo_client()
    else:
        try:
            from binance.exceptions import BinanceAPIException, BinanceRequestException
            from bot.client import get_client
            client = get_client()
        except EnvironmentError as e:
            print(f"✗ Config error: {e}", file=sys.stderr)
            print("  Tip: Run with --demo to try the bot without API keys.", file=sys.stderr)
            sys.exit(1)

    # ---------- place order ----------
    from bot.orders import place_order
    try:
        order = place_order(client, symbol, side, order_type, args.quantity, args.price)
        print_order_summary(order, demo=args.demo)
    except Exception as e:
        # In demo mode the mock client won't throw Binance errors,
        # but we keep a catch-all for safety.
        if not args.demo:
            try:
                from binance.exceptions import BinanceAPIException, BinanceRequestException
                if isinstance(e, BinanceAPIException):
                    print(f"✗ Binance rejected the order: {e.message}", file=sys.stderr)
                    print("  Tip: Check symbol name, quantity precision, or account balance.", file=sys.stderr)
                    sys.exit(1)
                elif isinstance(e, BinanceRequestException):
                    print("✗ Network error — couldn't reach Binance. Check your connection.", file=sys.stderr)
                    sys.exit(1)
            except ImportError:
                pass
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
