"""Tests for apartment trade API client"""

import pytest
import httpx
from unittest.mock import patch, AsyncMock
from data_go_mcp.apartment_trade.api_client import ApartmentTradeAPIClient


@pytest.fixture
def api_client():
    """Create API client with test API key"""
    return ApartmentTradeAPIClient(api_key="test-api-key")


@pytest.fixture
def mock_xml_response():
    """Sample XML response from API"""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
        </header>
        <body>
            <items>
                <item>
                    <sggCd>11680</sggCd>
                    <umdNm>삼성동</umdNm>
                    <aptNm>아이파크</aptNm>
                    <jibun>123</jibun>
                    <excluUseAr>84.95</excluUseAr>
                    <dealYear>2024</dealYear>
                    <dealMonth>1</dealMonth>
                    <dealDay>15</dealDay>
                    <dealAmount>150,000</dealAmount>
                    <floor>10</floor>
                    <buildYear>2010</buildYear>
                    <rgstDate>2024-01-20</rgstDate>
                </item>
                <item>
                    <sggCd>11680</sggCd>
                    <umdNm>청담동</umdNm>
                    <aptNm>래미안</aptNm>
                    <jibun>456</jibun>
                    <excluUseAr>120.50</excluUseAr>
                    <dealYear>2024</dealYear>
                    <dealMonth>1</dealMonth>
                    <dealDay>20</dealDay>
                    <dealAmount>200,000</dealAmount>
                    <floor>25</floor>
                    <buildYear>2015</buildYear>
                    <aptDong>101</aptDong>
                    <rgstDate>2024-01-25</rgstDate>
                </item>
            </items>
            <totalCount>2</totalCount>
            <numOfRows>10</numOfRows>
            <pageNo>1</pageNo>
        </body>
    </response>"""


@pytest.fixture
def mock_error_xml_response():
    """Sample error XML response from API"""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header>
            <resultCode>99</resultCode>
            <resultMsg>SERVICE ERROR</resultMsg>
        </header>
    </response>"""


@pytest.mark.asyncio
async def test_init_with_api_key():
    """Test client initialization with API key"""
    client = ApartmentTradeAPIClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade"
    await client.close()


@pytest.mark.asyncio
async def test_init_with_env_var():
    """Test client initialization with environment variable"""
    with patch.dict("os.environ", {"API_KEY": "env-test-key"}):
        client = ApartmentTradeAPIClient()
        assert client.api_key == "env-test-key"
        await client.close()


@pytest.mark.asyncio
async def test_init_without_api_key():
    """Test client initialization without API key raises error"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="API key is required"):
            ApartmentTradeAPIClient()


@pytest.mark.asyncio
async def test_get_apartment_trades_success(api_client, mock_xml_response):
    """Test successful apartment trade data retrieval"""
    with patch.object(api_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.text = mock_xml_response
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await api_client.get_apartment_trades(
            lawd_cd="11680",
            deal_ymd="202401"
        )
        
        assert "items" in result
        assert "totalCount" in result
        assert result["totalCount"] == 2
        
        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert "serviceKey=test-api-key" in call_url
        assert "LAWD_CD=11680" in call_url
        assert "DEAL_YMD=202401" in call_url
    
    await api_client.close()


@pytest.mark.asyncio
async def test_get_apartment_trades_api_error(api_client, mock_error_xml_response):
    """Test API error handling"""
    with patch.object(api_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.text = mock_error_xml_response
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="API Error \\[99\\]: SERVICE ERROR"):
            await api_client.get_apartment_trades(
                lawd_cd="11680",
                deal_ymd="202401"
            )
    
    await api_client.close()


@pytest.mark.asyncio
async def test_invalid_region_code(api_client):
    """Test validation of invalid region code"""
    with pytest.raises(ValueError, match="lawd_cd must be 5 digits"):
        await api_client.get_apartment_trades(
            lawd_cd="123",  # Too short
            deal_ymd="202401"
        )
    
    with pytest.raises(ValueError, match="lawd_cd must be 5 digits"):
        await api_client.get_apartment_trades(
            lawd_cd="123456",  # Too long
            deal_ymd="202401"
        )
    
    await api_client.close()


@pytest.mark.asyncio
async def test_invalid_year_month(api_client):
    """Test validation of invalid year-month"""
    with pytest.raises(ValueError, match="deal_ymd must be 6 digits"):
        await api_client.get_apartment_trades(
            lawd_cd="11680",
            deal_ymd="2024"  # Too short
        )
    
    with pytest.raises(ValueError, match="deal_ymd must be 6 digits"):
        await api_client.get_apartment_trades(
            lawd_cd="11680",
            deal_ymd="20240101"  # Too long
        )
    
    await api_client.close()


@pytest.mark.asyncio
async def test_search_by_region(api_client, mock_xml_response):
    """Test search_by_region convenience method"""
    with patch.object(api_client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.text = mock_xml_response
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await api_client.search_by_region(
            region_code="11680",
            year_month="202401",
            page=2,
            size=20
        )
        
        assert "items" in result
        
        # Verify pagination parameters
        call_url = mock_get.call_args[0][0]
        assert "pageNo=2" in call_url
        assert "numOfRows=20" in call_url
    
    await api_client.close()


@pytest.mark.asyncio
async def test_context_manager():
    """Test API client as context manager"""
    async with ApartmentTradeAPIClient(api_key="test-key") as client:
        assert client.api_key == "test-key"
        # Client should auto-close when exiting context