from binascii import a2b_base64
import httpx
import json
import os
import time
import hmac
import hashlib
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

URL = "https://api.binance.com/api/v3/"


def serialize_params(params):
    """Convert parameters to the appropriate format for Binance API."""
    result = {}
    for key, value in params.items():
        if isinstance(value, list):
            result[key] = json.dumps(value)
        elif value is not None:
            result[key] = value
    return result


async def exchange_info_of_a_symbol(symbol):
    """Get exchange information for a specific symbol."""
    # This endpoint has NONE security type
    params = {"symbol": symbol}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}exchangeInfo",
            params=params,
        )
        return json.dumps(response.json())


async def exchange_info_of_all_symbols():
    """Get exchange information for all symbols."""
    # This endpoint has NONE security type
    

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}exchangeInfo"
        )
        return response.json()


async def get_trade_data(symbol, interval, start_time=None, end_time=None, limit=None):
    """Get kline/candlestick data for a symbol."""
    # This endpoint has NONE security type
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": limit,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}klines",
            params=params,
        )
        return json.dumps(response.json())


async def agg_trades(symbol):
    """Get aggregate trades for a symbol."""
    # This endpoint has NONE security type
    params = {"symbol": symbol, "limit": 20}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}aggTrades",
            params=params,
        )
        return json.dumps(response.json())


async def trade_history(symbol):
    """Get recent trades for a symbol."""
    # This endpoint has USER_DATA security type
    params = {"symbol": symbol, "limit": 20}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}historicalTrades",
            params=params,
        )
        return json.dumps(response.json())


async def depth(symbol):
    """Get order book depth for a symbol."""
    # This endpoint has NONE security type
    params = {"symbol": symbol}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}depth",
            params=params,
        )
        return json.dumps(response.json())


async def current_avg_price(symbol):
    """Get current average price for a symbol."""
    # This endpoint has NONE security type
    params = {"symbol": symbol}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}avgPrice",
            params=params,
        )
        return json.dumps(response.json())


async def price_ticker_in_24hr(symbol):
    """Get 24hr price ticker for a symbol."""
    # This endpoint has NONE security type
    params = {"symbol": symbol}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker/24hr",
            params=params,
        )
        return json.dumps(response.json())


async def trading_day_ticker(symbols):
    """Get trading day ticker for symbols."""
    # This endpoint has NONE security type
    params = serialize_params({"symbols": symbols})

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker/tradingDay",
            params=params,
        )
        return json.dumps(response.json())


async def symbol_price_ticker(symbol=None, symbols=None):
    """Get symbol price ticker."""
    # This endpoint has NONE security type
    params = serialize_params({"symbol": symbol, "symbols": symbols})

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker/price",
            params=params,
        )
        return json.dumps(response.json())


async def symbol_order_book_ticker(symbol=None, symbols=None):
    """Get symbol order book ticker."""
    # This endpoint has NONE security type
    params = serialize_params({"symbol": symbol, "symbols": symbols})

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker/bookTicker",
            params=params,
        )
        return json.dumps(response.json())


async def rolling_window_ticker(
    symbol=None, symbols=None, window_size=None, type_=None
):
    """Get rolling window price change statistics.

    Args:
        symbol: Symbol to get data for
        symbols: List of symbols to get data for
        window_size: Window size, e.g. "1d"
        type_: Type of response, either "FULL" or "MINI"
    """
    # This endpoint has NONE security type
    params = serialize_params(
        {"symbol": symbol, "symbols": symbols, "windowSize": window_size, "type": type_}
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker",
            params=params,
        )
        return json.dumps(response.json())



# API key and secret from environment variables
api_key = os.environ.get("BINANCE_API_KEY", "")
api_secret = os.environ.get("BINANCE_API_SECRET", "")

# Check if API credentials are available
if not api_key or not api_secret:
    logger.error("Binance API credentials not found in environment variables")
    logger.info("Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")



async def get_user_data(omit_zero_balances=False, recv_window=5000):
    """Get current account information.
    
    Args:
        omit_zero_balances: When set to true, emits only the non-zero balances of an account.
        recv_window: The value cannot be greater than 60000
    
    Returns:
        JSON string with account information
    """
    # Create parameters dictionary with required parameters
    params = {
        'timestamp': int(time.time() * 1000),  # Current timestamp in milliseconds (required)
        'recvWindow': recv_window,
        'omitZeroBalances': 'true'
    }
    
    # Add optional parameter if enabled
    if omit_zero_balances:
        params['omitZeroBalances'] = 'true'
    
    # Create query string from parameters
    query_string = '&'.join([f"{key}={params[key]}" for key in params])
    
    # Generate signature
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Add signature to parameters
    params['signature'] = signature
    
    # Set API key in headers
    headers = {
        "X-MBX-APIKEY": api_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{URL}account",
                params=params,
                headers=headers
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.json() if e.response.headers.get('content-type') == 'application/json' else e.response.text
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    
import asyncio


async def put_order(
    symbol,
    side,
    type_,
    time_in_force,
    quantity,
    price
):
    """Place a test order on Binance.
    
    This uses the POST /api/v3/order/test endpoint which validates a new order
    without actually placing it on the market.
    """
    params = {
    'symbol': symbol,
    'side': side,
    'type': type_,
    'timeInForce': time_in_force,
    'quantity': quantity,
    'price': price,
    'timestamp': int(time.time() * 1000),
    'recvWindow': 5000
}
    query_string = '&'.join([f"{key}={params[key]}" for key in params])
    
    # Generate signature
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    headers = {
        "X-MBX-APIKEY": api_key
    }
    
    try:
        logger.info(f"Sending order test request with params: {params}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{URL}order/test",  # Using the test endpoint to avoid actual order
                params=params,
                headers=headers
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.json() if e.response.headers.get('content-type') == 'application/json' else e.response.text
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
if __name__ == "__main__":
    import asyncio
    async def main():
        # First, check if API credentials are available
        if not api_key or not api_secret:
            print(json.dumps({
                "error": "API credentials missing",
                "details": "Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables"
            }, indent=2))
            return
            
        try:
            # Get current price for XRPUSDT
            price_info = await symbol_price_ticker(symbol='XRPUSDT')
            price_data = json.loads(price_info)
            
            if isinstance(price_data, dict) and 'price' in price_data:
                current_price = float(price_data['price'])
                logger.info(f"Current XRPUSDT price: {current_price}")
                
                # Calculate a valid price (5% below current price)
                buy_price = current_price * 0.95
                buy_price = round(buy_price / 0.0001) * 0.0001  # Round to nearest tickSize (0.0001)
                
                # Using valid quantity for XRPUSDT (minimum 0.1, in increments of 0.1)
                quantity = 10.0  # This is a valid quantity for XRPUSDT
                
                logger.info(f"Placing test order: XRPUSDT BUY {quantity} @ {buy_price}")
                result = await put_order("XRPUSDT", "BUY", "LIMIT", "GTC", quantity, buy_price)
                print(result)
            else:
                print(json.dumps({
                    "error": "Failed to get current price",
                    "details": price_info
                }, indent=2))
        except Exception as e:
            error_msg = json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
            print(error_msg)
            return error_msg
    asyncio.run(main())
    