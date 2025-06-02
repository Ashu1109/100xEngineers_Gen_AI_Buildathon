import asyncio
import json
from apis import symbol_price_ticker

async def main():
    result = await symbol_price_ticker(symbol='XRPUSDT')
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
