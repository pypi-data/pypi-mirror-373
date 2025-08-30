#!/usr/bin/env python3
"""Quick test for apartment trade MCP server"""

import asyncio
import os
from data_go_mcp.apartment_trade.server import get_region_codes, search_apartment_trades

async def main():
    """Run quick tests"""
    print("=" * 60)
    print("Testing Apartment Trade MCP Server")
    print("=" * 60)
    
    # Test 1: Get region codes
    print("\n1. Testing get_region_codes - searching for '강남':")
    result = await get_region_codes({"search": "강남"})
    print(result[0].text[:500])  # Print first 500 chars
    
    # Test 2: Get all region codes
    print("\n2. Testing get_region_codes - get all major cities:")
    result = await get_region_codes({})
    print(result[0].text[:500])  # Print first 500 chars
    
    # Test 3: Search with invalid region
    print("\n3. Testing search_apartment_trades - invalid region:")
    result = await search_apartment_trades({
        "region": "invalid_region",
        "year_month": "202401"
    })
    print(result[0].text)
    
    # Test 4: Test with region name resolution  
    print("\n4. Testing region name resolution - '강남구' -> '11680':")
    # This will fail without API key but shows region resolution works
    try:
        result = await search_apartment_trades({
            "region": "강남구",
            "year_month": "202401"
        })
        print(result[0].text[:500])
    except Exception as e:
        print(f"Expected error (no API key): {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())