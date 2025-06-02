from mcp.server.fastmcp import FastMCP
import json
import re
from typing import Optional, List, Dict, Any
from apis import (
    exchange_info_of_a_symbol,
    exchange_info_of_all_symbols,
    get_trade_data,
    agg_trades,
    trade_history,
    depth,
    current_avg_price,
    price_ticker_in_24hr,
    trading_day_ticker,
    symbol_price_ticker,
    symbol_order_book_ticker,
    put_order,
    rolling_window_ticker,
)
from screen_shot import take_screenshot


mcp = FastMCP("TradeAssistant", "0.1.0")


@mcp.tool()
async def bb7_ExchangeInfoOfASymbole(symbol: str):
    """
    Get exchange information for a specific symbol.

    Args:
        symbol: The symbol to get information for (e.g. "BTCUSDT")

    Returns:
        Exchange information for the specified symbol
    """
    data = await exchange_info_of_a_symbol(symbol)
    return data


@mcp.tool()
async def bb7_ExchangeInfoOfAllSymbole():
    """
    Get exchange information for all symbols.

    Returns:
        Exchange information for all symbols
    """
    data = await exchange_info_of_all_symbols()
    return json.dumps(data)


@mcp.tool()
async def bb7_getTradeData(
    symbol: str,
    interval: str,
    startTime: Optional[int] = None,
    endTime: Optional[int] = None,
    limit: Optional[int] = None,
):
    """
    Get kline/candlestick data for a symbol.

    Args:
        symbol: The symbol to get trades for (e.g. "BTCUSDT")
        interval: The interval for the kline data (e.g. "1m", "1h", "1d")
        startTime: Optional start time in milliseconds
        endTime: Optional end time in milliseconds
        limit: Optional limit of records to return

    Returns:
        Kline/candlestick data for the specified symbol and interval
    """
    try:
        # Convert parameter names from camelCase to snake_case to match get_trade_data function
        data = await get_trade_data(symbol, interval, start_time=startTime, end_time=endTime, limit=limit)
        return data
    except Exception as e:
        # Handle any errors that occur during execution
        import traceback
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        return json.dumps({"error": error_message})


@mcp.tool()
async def bb7_AggTrades(symbol: str):
    """
    Get aggregate trades for a symbol.

    Args:
        symbol: The symbol to get trades for (e.g. "BTCUSDT")

    Returns:
        Aggregate trades for the specified symbol
    """
    data = await agg_trades(symbol)
    return data


@mcp.tool()
async def bb7_TradeHistory(symbol: str):
    """
    Get recent trades for a symbol.

    Args:
        symbol: The symbol to get trade history for (e.g. "BTCUSDT")

    Returns:
        Recent trades for the specified symbol
    """
    data = await trade_history(symbol)
    return data


@mcp.tool()
async def bb7_Depth(symbol: str):
    """
    Get order book depth for a symbol.

    Args:
        symbol: The symbol to get depth for (e.g. "BTCUSDT")

    Returns:
        Order book depth for the specified symbol
    """
    data = await depth(symbol)
    return data


@mcp.tool()
async def bb7_CurrentAvgPrice(symbol: str):
    """
    Get current average price for a symbol.

    Args:
        symbol: The symbol to get average price for (e.g. "BTCUSDT")

    Returns:
        Current average price for the specified symbol
    """
    data = await current_avg_price(symbol)
    return data


@mcp.tool()
async def bb7_PriceTickerIn24Hr(symbol: str):
    """
    Get 24hr price ticker for a symbol.

    Args:
        symbol: The symbol to get 24hr price ticker for (e.g. "BTCUSDT")

    Returns:
        24hr price ticker for the specified symbol
    """
    data = await price_ticker_in_24hr(symbol)
    return data


@mcp.tool()
async def bb7_TradingDayTicker(symbols: List[str]):
    """
    Get trading day ticker for symbols.

    Args:
        symbols: List of symbols to get trading day ticker for

    Returns:
        Trading day ticker for the specified symbols
    """
    data = await trading_day_ticker(symbols)
    return data


@mcp.tool()
async def bb7_SymbolPriceTicker(
    symbol: Optional[str] = None, symbols: Optional[List[str]] = None
):
    """
    Get symbol price ticker.

    Args:
        symbol: Optional single symbol to get price ticker for
        symbols: Optional list of symbols to get price ticker for

    Returns:
        Symbol price ticker for the specified symbol(s)
    """
    data = await symbol_price_ticker(symbol, symbols)
    return data


@mcp.tool()
async def bb7_SymbolOrderBookTicker(
    symbol: Optional[str] = None, symbols: Optional[List[str]] = None
):
    """
    Get symbol order book ticker.

    Args:
        symbol: Optional single symbol to get order book ticker for
        symbols: Optional list of symbols to get order book ticker for

    Returns:
        Symbol order book ticker for the specified symbol(s)
    """
    data = await symbol_order_book_ticker(symbol, symbols)
    return data


@mcp.tool()
async def bb7_RollingWindowTicker(
    symbol: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    windowSize: Optional[str] = None,
    type: Optional[str] = None,
):
    """
    Get rolling window price change statistics.

    Args:
        symbol: Optional symbol to get data for
        symbols: Optional list of symbols to get data for
        windowSize: Optional window size, e.g. "1d"
        type: Optional type of response, either "FULL" or "MINI"

    Returns:
        Rolling window price change statistics for the specified symbol(s)
    """
    data = await rolling_window_ticker(symbol, symbols, windowSize, type)
    return data


@mcp.tool()
async def takeScreenShotOfTarde(chart_url):
    """
    Take a screenshot of the chart.
    https://www.tradingview.com/chart/YiBYLtYW/?symbol=CRYPTO%3A{symbol}

    EXAMPLE SYMBOL = BTCUSD

    TAKE SYMBOL ACCORDING TO THE USER AND TAKE SCREENSHOT OF THAT CHART
    CHANGE SYMBOL IN URL ACCORDING TO THE USER

    Args:
        chart_url: URL of the chart to take a screenshot of

    Returns:
         Array of Screenshot URL of the chart
    """
    return take_screenshot(chart_url)

@mcp.tool()
async def bb7_PutOrder(
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
    data = await put_order(symbol, side, type_, time_in_force, quantity, price)
    return data

mcp.run(transport="stdio")
