import asyncio
import json
from apis import exchange_info_of_a_symbol

async def main():
    result = await exchange_info_of_a_symbol('XRPUSDT')
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
