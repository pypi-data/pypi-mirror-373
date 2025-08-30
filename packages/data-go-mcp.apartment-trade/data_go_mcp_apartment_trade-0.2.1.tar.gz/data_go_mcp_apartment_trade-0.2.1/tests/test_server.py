"""Tests for apartment trade MCP server"""

import pytest
from unittest.mock import patch, AsyncMock
from mcp.types import TextContent
from data_go_mcp.apartment_trade.server import (
    list_tools,
    call_tool,
    search_apartment_trades,
    get_region_codes,
    REGION_CODES
)


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are properly listed"""
    tools = await list_tools()
    
    assert len(tools) == 2
    
    # Check search_apartment_trades tool
    search_tool = tools[0]
    assert search_tool.name == "search_apartment_trades"
    assert "아파트 매매 실거래가" in search_tool.description
    assert "region" in search_tool.inputSchema["properties"]
    assert "year_month" in search_tool.inputSchema["properties"]
    
    # Check get_region_codes tool
    codes_tool = tools[1]
    assert codes_tool.name == "get_region_codes"
    assert "지역코드 조회" in codes_tool.description


@pytest.mark.asyncio
async def test_get_region_codes_all():
    """Test getting all region codes"""
    result = await get_region_codes({})
    
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    text = result[0].text
    assert "한국 주요 지역코드" in text
    assert "서울" in text
    assert "11000" in text
    assert "부산" in text
    assert "26000" in text


@pytest.mark.asyncio
async def test_get_region_codes_search():
    """Test searching for specific region codes"""
    result = await get_region_codes({"search": "강남"})
    
    assert len(result) == 1
    text = result[0].text
    assert "강남" in text
    assert "11680" in text
    assert "검색 결과" in text


@pytest.mark.asyncio
async def test_get_region_codes_no_match():
    """Test searching with no matches"""
    result = await get_region_codes({"search": "invalid_region"})
    
    assert len(result) == 1
    text = result[0].text
    assert "찾을 수 없습니다" in text


@pytest.mark.asyncio
async def test_search_apartment_trades_with_region_name():
    """Test searching with region name instead of code"""
    mock_response_data = {
        "items": {
            "item": [
                {
                    "sggCd": "11680",
                    "umdNm": "삼성동",
                    "aptNm": "아이파크",
                    "dealAmount": "150000",
                    "dealYear": "2024",
                    "dealMonth": "1",
                    "dealDay": "15"
                }
            ]
        },
        "totalCount": 1,
        "numOfRows": 10,
        "pageNo": 1
    }
    
    with patch("data_go_mcp.apartment_trade.server.ApartmentTradeAPIClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.search_by_region.return_value = mock_response_data
        mock_client.return_value = mock_instance
        
        result = await search_apartment_trades({
            "region": "강남구",
            "year_month": "202401"
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "아파트 매매 실거래가 검색 결과" in text
        assert "아이파크" in text
        assert "삼성동" in text
        
        # Verify API was called with resolved region code
        mock_instance.search_by_region.assert_called_once_with(
            region_code="11680",
            year_month="202401",
            page=1,
            size=10
        )


@pytest.mark.asyncio
async def test_search_apartment_trades_with_region_code():
    """Test searching with region code directly"""
    mock_response_data = {
        "items": {
            "item": []
        },
        "totalCount": 0,
        "numOfRows": 10,
        "pageNo": 1
    }
    
    with patch("data_go_mcp.apartment_trade.server.ApartmentTradeAPIClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.search_by_region.return_value = mock_response_data
        mock_client.return_value = mock_instance
        
        result = await search_apartment_trades({
            "region": "11680",
            "year_month": "202401"
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "거래 정보가 없습니다" in text


@pytest.mark.asyncio
async def test_search_apartment_trades_invalid_region():
    """Test searching with invalid region"""
    result = await search_apartment_trades({
        "region": "invalid_region",
        "year_month": "202401"
    })
    
    assert len(result) == 1
    text = result[0].text
    assert "지역을 찾을 수 없습니다" in text


@pytest.mark.asyncio
async def test_search_apartment_trades_invalid_input():
    """Test searching with invalid input format"""
    result = await search_apartment_trades({
        "region": "11680",
        "year_month": "2024"  # Invalid format
    })
    
    assert len(result) == 1
    text = result[0].text
    assert "입력값 오류" in text


@pytest.mark.asyncio
async def test_search_apartment_trades_with_pagination():
    """Test searching with pagination parameters"""
    mock_response_data = {
        "items": {
            "item": [
                {
                    "aptNm": "아파트1",
                    "dealAmount": "100000"
                },
                {
                    "aptNm": "아파트2",
                    "dealAmount": "200000"
                }
            ]
        },
        "totalCount": 50,
        "numOfRows": 2,
        "pageNo": 3
    }
    
    with patch("data_go_mcp.apartment_trade.server.ApartmentTradeAPIClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.search_by_region.return_value = mock_response_data
        mock_client.return_value = mock_instance
        
        result = await search_apartment_trades({
            "region": "11680",
            "year_month": "202401",
            "page": 3,
            "size": 2
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "페이지: 3/" in text
        assert "page를 4로 설정하세요" in text  # Has more pages
        
        # Verify pagination parameters were passed
        mock_instance.search_by_region.assert_called_once_with(
            region_code="11680",
            year_month="202401",
            page=3,
            size=2
        )


@pytest.mark.asyncio
async def test_search_apartment_trades_api_error():
    """Test handling of API errors"""
    with patch("data_go_mcp.apartment_trade.server.ApartmentTradeAPIClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.search_by_region.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        result = await search_apartment_trades({
            "region": "11680",
            "year_month": "202401"
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "API 호출 실패" in text
        assert "API Error" in text


@pytest.mark.asyncio
async def test_call_tool_search():
    """Test call_tool with search_apartment_trades"""
    with patch("data_go_mcp.apartment_trade.server.search_apartment_trades") as mock_search:
        mock_search.return_value = [TextContent(type="text", text="Search results")]
        
        result = await call_tool("search_apartment_trades", {"region": "강남구", "year_month": "202401"})
        
        assert len(result) == 1
        assert result[0].text == "Search results"
        mock_search.assert_called_once_with({"region": "강남구", "year_month": "202401"})


@pytest.mark.asyncio
async def test_call_tool_get_codes():
    """Test call_tool with get_region_codes"""
    with patch("data_go_mcp.apartment_trade.server.get_region_codes") as mock_get:
        mock_get.return_value = [TextContent(type="text", text="Region codes")]
        
        result = await call_tool("get_region_codes", {"search": "서울"})
        
        assert len(result) == 1
        assert result[0].text == "Region codes"
        mock_get.assert_called_once_with({"search": "서울"})


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test call_tool with unknown tool name"""
    result = await call_tool("unknown_tool", {})
    
    assert len(result) == 1
    assert "Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_error():
    """Test call_tool error handling"""
    with patch("data_go_mcp.apartment_trade.server.search_apartment_trades") as mock_search:
        mock_search.side_effect = Exception("Test error")
        
        result = await call_tool("search_apartment_trades", {"region": "11680", "year_month": "202401"})
        
        assert len(result) == 1
        assert "Error: Test error" in result[0].text


def test_region_codes_completeness():
    """Test that major region codes are included"""
    # Test major cities
    assert "서울" in REGION_CODES
    assert "부산" in REGION_CODES
    assert "대구" in REGION_CODES
    assert "인천" in REGION_CODES
    
    # Test Seoul districts
    assert "강남구" in REGION_CODES
    assert "서초구" in REGION_CODES
    assert "송파구" in REGION_CODES
    
    # Test Gyeonggi cities
    assert "수원시" in REGION_CODES
    assert "성남시" in REGION_CODES
    assert "용인시" in REGION_CODES
    
    # Test code format
    for name, code in REGION_CODES.items():
        assert len(code) == 5
        assert code.isdigit()