"""API client for apartment trade data from data.go.kr"""

import os
from typing import Dict, Any, Optional
import httpx
import xmltodict
from urllib.parse import urlencode, quote

class ApartmentTradeAPIClient:
    """Client for Korea apartment trade API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize API client
        
        Args:
            api_key: API key for authentication. If not provided, looks for API_KEY env var
        """
        self.api_key = api_key or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set API_KEY environment variable or pass api_key parameter")
        
        self.base_url = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def get_apartment_trades(
        self,
        lawd_cd: str,
        deal_ymd: str,
        page_no: int = 1,
        num_of_rows: int = 10
    ) -> Dict[str, Any]:
        """Get apartment trade data for a specific region and period
        
        Args:
            lawd_cd: 지역코드 (법정동코드 앞 5자리, e.g., "11110" for 서울 종로구)
            deal_ymd: 계약년월 (YYYYMM format, e.g., "202401")
            page_no: Page number (default: 1)
            num_of_rows: Number of rows per page (default: 10)
        
        Returns:
            Parsed API response as dictionary
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response cannot be parsed
        """
        # Validate inputs
        if not lawd_cd or len(lawd_cd) != 5:
            raise ValueError("lawd_cd must be 5 digits (e.g., '11110')")
        
        if not deal_ymd or len(deal_ymd) != 6:
            raise ValueError("deal_ymd must be 6 digits in YYYYMM format (e.g., '202401')")
        
        # Build request parameters
        params = {
            "serviceKey": self.api_key,
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows)
        }
        
        # Make API request
        url = f"{self.base_url}/getRTMSDataSvcAptTrade"
        
        try:
            # Build URL with proper encoding for the service key
            query_parts = []
            for key, value in params.items():
                if key == "serviceKey":
                    # Don't encode the service key
                    query_parts.append(f"{key}={value}")
                else:
                    query_parts.append(f"{key}={quote(str(value))}")
            
            full_url = f"{url}?{'&'.join(query_parts)}"
            
            response = await self.client.get(full_url)
            response.raise_for_status()
            
            # Parse XML response
            data = xmltodict.parse(response.text)
            
            # Check for API errors in the response
            if "response" in data:
                response_data = data["response"]
                
                # Check header for errors
                if "header" in response_data:
                    header = response_data["header"]
                    result_code = header.get("resultCode", "")
                    result_msg = header.get("resultMsg", "")
                    
                    if result_code != "00":
                        raise ValueError(f"API Error [{result_code}]: {result_msg}")
                
                # Extract body data
                if "body" in response_data:
                    return response_data["body"]
            
            return data
            
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"Failed to fetch apartment trade data: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
    
    async def search_by_region(
        self,
        region_code: str,
        year_month: str,
        page: int = 1,
        size: int = 10
    ) -> Dict[str, Any]:
        """Search apartment trades by region code and year-month
        
        This is a convenience method that wraps get_apartment_trades
        
        Args:
            region_code: 5-digit region code
            year_month: Year and month in YYYYMM format
            page: Page number (1-based)
            size: Page size
        
        Returns:
            API response data
        """
        return await self.get_apartment_trades(
            lawd_cd=region_code,
            deal_ymd=year_month,
            page_no=page,
            num_of_rows=size
        )