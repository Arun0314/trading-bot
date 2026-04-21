import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger()


def get_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise EnvironmentError(
            "Missing BINANCE_API_KEY or BINANCE_API_SECRET in .env"
        )

    # futures_testnet=True routes to testnet automatically
    client = Client(api_key, api_secret, testnet=True)
    logger.debug("Binance testnet client initialized")
    return client
