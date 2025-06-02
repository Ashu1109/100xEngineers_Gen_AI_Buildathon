import asyncio
import json
import os
import hmac
import hashlib
import time
import httpx
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

# API key and secret from environment variables
api_key = os.environ.get("BINANCE_API_KEY", "")
api_secret = os.environ.get("BINANCE_API_SECRET", "")

async def test_api_key():
    """Test if the API key has basic permissions by checking account status."""
    # Create parameters dictionary with required parameters
    params = {
        'timestamp': int(time.time() * 1000),  # Current timestamp in milliseconds
        'recvWindow': 5000
    }
    
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
        logger.info(f"Testing API key with params: {params}")
        async with httpx.AsyncClient() as client:
            # Try to access account information (requires API key with read permissions)
            response = await client.get(
                "https://api.binance.com/api/v3/account",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("API key is valid and has account read permissions")
                return json.dumps({"success": True, "message": "API key is valid"})
            else:
                logger.error(f"API key test failed with status code: {response.status_code}")
                return json.dumps({
                    "error": f"HTTP error: {response.status_code}",
                    "details": response.json() if response.headers.get('content-type') == 'application/json' else response.text
                }, indent=2)
    except Exception as e:
        logger.error(f"API key test failed with error: {str(e)}")
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)

async def main():
    if not api_key or not api_secret:
        print(json.dumps({
            "error": "API credentials missing",
            "details": "Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables"
        }, indent=2))
        return
        
    result = await test_api_key()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
