"""Tests for apartment trade data models"""

import pytest
from data_go_mcp.apartment_trade.models import (
    ApartmentTradeItem,
    ApartmentTradeItems,
    ApartmentTradeResponse,
    SearchRequest
)


def test_apartment_trade_item_basic():
    """Test basic apartment trade item creation"""
    item = ApartmentTradeItem(
        sggCd="11680",
        umdNm="삼성동",
        aptNm="아이파크",
        jibun="123",
        excluUseAr="84.95",
        dealYear="2024",
        dealMonth="1",
        dealDay="15",
        dealAmount="150,000",
        floor="10",
        buildYear="2010"
    )
    
    assert item.sgg_cd == "11680"
    assert item.umd_nm == "삼성동"
    assert item.apt_nm == "아이파크"
    assert item.deal_amount == "150000"  # Commas removed
    assert item.exclu_use_ar == "84.95"


def test_apartment_trade_item_aliases():
    """Test that field aliases work correctly"""
    data = {
        "sggCd": "11680",
        "umdNm": "삼성동",
        "aptNm": "아이파크",
        "dealAmount": "150,000"
    }
    
    item = ApartmentTradeItem(**data)
    assert item.sgg_cd == "11680"
    assert item.umd_nm == "삼성동"
    assert item.apt_nm == "아이파크"
    assert item.deal_amount == "150000"


def test_deal_amount_cleaning():
    """Test that deal amount is cleaned of commas and whitespace"""
    item = ApartmentTradeItem(dealAmount=" 150,000 ")
    assert item.deal_amount == "150000"


def test_deal_date_property():
    """Test deal_date property formatting"""
    item = ApartmentTradeItem(
        dealYear="2024",
        dealMonth="1",
        dealDay="5"
    )
    assert item.deal_date == "2024-01-05"
    
    # Test with missing data
    item2 = ApartmentTradeItem(dealYear="2024")
    assert item2.deal_date is None


def test_deal_amount_int_property():
    """Test deal_amount_int property conversion"""
    item = ApartmentTradeItem(dealAmount="150000")
    assert item.deal_amount_int == 150000
    
    # Test with invalid amount
    item2 = ApartmentTradeItem(dealAmount="invalid")
    assert item2.deal_amount_int is None
    
    # Test with None
    item3 = ApartmentTradeItem()
    assert item3.deal_amount_int is None


def test_exclu_use_ar_float_property():
    """Test exclusive use area float conversion"""
    item = ApartmentTradeItem(excluUseAr="84.95")
    assert item.exclu_use_ar_float == 84.95
    
    # Test with invalid value
    item2 = ApartmentTradeItem(excluUseAr="invalid")
    assert item2.exclu_use_ar_float is None


def test_apartment_trade_items_single():
    """Test ApartmentTradeItems with single item"""
    item = ApartmentTradeItem(aptNm="아이파크")
    items_container = ApartmentTradeItems(item=item)
    
    assert len(items_container.items) == 1
    assert items_container.items[0].apt_nm == "아이파크"


def test_apartment_trade_items_list():
    """Test ApartmentTradeItems with list of items"""
    item1 = ApartmentTradeItem(aptNm="아이파크")
    item2 = ApartmentTradeItem(aptNm="래미안")
    items_container = ApartmentTradeItems(item=[item1, item2])
    
    assert len(items_container.items) == 2
    assert items_container.items[0].apt_nm == "아이파크"
    assert items_container.items[1].apt_nm == "래미안"


def test_apartment_trade_items_none():
    """Test ApartmentTradeItems with None"""
    items_container = ApartmentTradeItems(item=None)
    assert len(items_container.items) == 0


def test_apartment_trade_response():
    """Test apartment trade response model"""
    item1 = ApartmentTradeItem(aptNm="아이파크")
    item2 = ApartmentTradeItem(aptNm="래미안")
    items_container = ApartmentTradeItems(item=[item1, item2])
    
    response = ApartmentTradeResponse(
        items=items_container,
        totalCount=100,
        numOfRows=10,
        pageNo=1
    )
    
    assert response.total_count == 100
    assert response.num_of_rows == 10
    assert response.page_no == 1
    assert len(response.trade_items) == 2


def test_apartment_trade_response_has_more():
    """Test has_more property of response"""
    response = ApartmentTradeResponse(
        totalCount=100,
        numOfRows=10,
        pageNo=1
    )
    assert response.has_more is True  # 1 * 10 < 100
    
    response2 = ApartmentTradeResponse(
        totalCount=100,
        numOfRows=10,
        pageNo=10
    )
    assert response2.has_more is False  # 10 * 10 >= 100
    
    response3 = ApartmentTradeResponse()
    assert response3.has_more is False  # No data


def test_search_request_valid():
    """Test valid search request"""
    request = SearchRequest(
        region_code="11680",
        year_month="202401",
        page=1,
        size=10
    )
    
    assert request.region_code == "11680"
    assert request.year_month == "202401"
    assert request.page == 1
    assert request.size == 10


def test_search_request_defaults():
    """Test search request default values"""
    request = SearchRequest(
        region_code="11680",
        year_month="202401"
    )
    
    assert request.page == 1
    assert request.size == 10


def test_search_request_invalid_region_code():
    """Test invalid region code validation"""
    with pytest.raises(ValueError, match="Region code must be 5 digits"):
        SearchRequest(
            region_code="123",  # Too short
            year_month="202401"
        )
    
    with pytest.raises(ValueError, match="Region code must be 5 digits"):
        SearchRequest(
            region_code="abcde",  # Not digits
            year_month="202401"
        )


def test_search_request_invalid_year_month():
    """Test invalid year-month validation"""
    with pytest.raises(ValueError, match="Year-month must be 6 digits"):
        SearchRequest(
            region_code="11680",
            year_month="2024"  # Too short
        )
    
    with pytest.raises(ValueError, match="Month must be between 01 and 12"):
        SearchRequest(
            region_code="11680",
            year_month="202413"  # Invalid month
        )
    
    with pytest.raises(ValueError, match="Year must be between 2006"):
        SearchRequest(
            region_code="11680",
            year_month="200501"  # Too old
        )


def test_search_request_invalid_pagination():
    """Test invalid pagination parameters"""
    with pytest.raises(ValueError):
        SearchRequest(
            region_code="11680",
            year_month="202401",
            page=0  # Must be >= 1
        )
    
    with pytest.raises(ValueError):
        SearchRequest(
            region_code="11680",
            year_month="202401",
            size=101  # Max is 100
        )


def test_complete_item_with_all_fields():
    """Test apartment trade item with all optional fields"""
    item = ApartmentTradeItem(
        sggCd="11680",
        umdNm="삼성동",
        aptNm="아이파크",
        aptDong="101",
        jibun="123",
        excluUseAr="84.95",
        dealYear="2024",
        dealMonth="1",
        dealDay="15",
        dealAmount="150,000",
        floor="10",
        buildYear="2010",
        cdealType="N",
        cdealDay="",
        dealingGbn="중개거래",
        estateAgentSggNm="강남구",
        rgstDate="2024-01-20",
        slerGbn="개인",
        buyerGbn="개인",
        landLeaseholdGbn=""
    )
    
    assert item.apt_dong == "101"
    assert item.estate_agent_sgg_nm == "강남구"
    assert item.sler_gbn == "개인"
    assert item.buyer_gbn == "개인"