#!/usr/bin/env python3
"""MCP server for Korea apartment trade data from data.go.kr"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import ApartmentTradeAPIClient
from .models import ApartmentTradeResponse, SearchRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version
__version__ = "0.1.0"

# Create MCP server instance
mcp = Server("data-go-mcp.apartment-trade")

# Region codes for major cities in Korea
REGION_CODES = {
    # 서울특별시
    "서울": "11000",
    "종로구": "11110",
    "중구": "11140",
    "용산구": "11170",
    "성동구": "11200",
    "광진구": "11215",
    "동대문구": "11230",
    "중랑구": "11260",
    "성북구": "11290",
    "강북구": "11305",
    "도봉구": "11320",
    "노원구": "11350",
    "은평구": "11380",
    "서대문구": "11410",
    "마포구": "11440",
    "양천구": "11470",
    "강서구": "11500",
    "구로구": "11530",
    "금천구": "11545",
    "영등포구": "11560",
    "동작구": "11590",
    "관악구": "11620",
    "서초구": "11650",
    "강남구": "11680",
    "송파구": "11710",
    "강동구": "11740",
    
    # 부산광역시
    "부산": "26000",
    "부산중구": "26110",
    "부산서구": "26140",
    "부산동구": "26170",
    "부산영도구": "26200",
    "부산진구": "26230",
    "부산동래구": "26260",
    "부산남구": "26290",
    "부산북구": "26320",
    "부산해운대구": "26350",
    "부산사하구": "26380",
    "부산금정구": "26410",
    "부산강서구": "26440",
    "부산연제구": "26470",
    "부산수영구": "26500",
    "부산사상구": "26530",
    "부산기장군": "26710",
    
    # 대구광역시
    "대구": "27000",
    "대구중구": "27110",
    "대구동구": "27140",
    "대구서구": "27170",
    "대구남구": "27200",
    "대구북구": "27230",
    "대구수성구": "27260",
    "대구달서구": "27290",
    "대구달성군": "27710",
    
    # 인천광역시
    "인천": "28000",
    "인천중구": "28110",
    "인천동구": "28140",
    "인천미추홀구": "28177",
    "인천연수구": "28185",
    "인천남동구": "28200",
    "인천부평구": "28237",
    "인천계양구": "28245",
    "인천서구": "28260",
    "인천강화군": "28710",
    "인천옹진군": "28720",
    
    # 광주광역시
    "광주": "29000",
    "광주동구": "29110",
    "광주서구": "29140",
    "광주남구": "29155",
    "광주북구": "29170",
    "광주광산구": "29200",
    
    # 대전광역시
    "대전": "30000",
    "대전동구": "30110",
    "대전중구": "30140",
    "대전서구": "30170",
    "대전유성구": "30200",
    "대전대덕구": "30230",
    
    # 울산광역시
    "울산": "31000",
    "울산중구": "31110",
    "울산남구": "31140",
    "울산동구": "31170",
    "울산북구": "31200",
    "울산울주군": "31710",
    
    # 세종특별자치시
    "세종": "36110",
    
    # 경기도 주요 도시
    "수원시": "41110",
    "수원시장안구": "41111",
    "수원시권선구": "41113",
    "수원시팔달구": "41115",
    "수원시영통구": "41117",
    "성남시": "41130",
    "성남시수정구": "41131",
    "성남시중원구": "41133",
    "성남시분당구": "41135",
    "의정부시": "41150",
    "안양시": "41170",
    "안양시만안구": "41171",
    "안양시동안구": "41173",
    "부천시": "41190",
    "광명시": "41210",
    "평택시": "41220",
    "동두천시": "41250",
    "안산시": "41270",
    "안산시상록구": "41271",
    "안산시단원구": "41273",
    "고양시": "41280",
    "고양시덕양구": "41281",
    "고양시일산동구": "41285",
    "고양시일산서구": "41287",
    "과천시": "41290",
    "구리시": "41310",
    "남양주시": "41360",
    "오산시": "41370",
    "시흥시": "41390",
    "군포시": "41410",
    "의왕시": "41430",
    "하남시": "41450",
    "용인시": "41460",
    "용인시처인구": "41461",
    "용인시기흥구": "41463",
    "용인시수지구": "41465",
    "파주시": "41480",
    "이천시": "41500",
    "안성시": "41550",
    "김포시": "41570",
    "화성시": "41590",
    "광주시": "41610",
    "양주시": "41630",
    "포천시": "41650",
    "여주시": "41670",
}


@mcp.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_apartment_trades",
            description="아파트 매매 실거래가 검색 - Search apartment trade transactions by region and period. 지역코드와 거래년월로 아파트 매매 실거래 정보를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": f"지역명 또는 지역코드. 예시: '강남구', '11680', '서울'. 지원 지역: {', '.join(list(REGION_CODES.keys())[:10])}..."
                    },
                    "year_month": {
                        "type": "string",
                        "description": "거래년월 (YYYYMM format). 예시: '202401' for January 2024"
                    },
                    "page": {
                        "type": "integer",
                        "description": "페이지 번호 (기본값: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "size": {
                        "type": "integer",
                        "description": "페이지당 결과 수 (기본값: 10, 최대: 100)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["region", "year_month"]
            }
        ),
        Tool(
            name="get_region_codes",
            description="지역코드 조회 - Get region codes for Korean cities and districts. 한국의 시/군/구 지역코드를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "검색할 지역명 (선택사항). 예시: '서울', '강남', '부산'"
                    }
                },
                "required": []
            }
        )
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "search_apartment_trades":
            return await search_apartment_trades(arguments)
        elif name == "get_region_codes":
            return await get_region_codes(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def search_apartment_trades(arguments: Dict[str, Any]) -> List[TextContent]:
    """Search apartment trade transactions"""
    
    # Extract arguments
    region = arguments.get("region", "")
    year_month = arguments.get("year_month", "")
    page = arguments.get("page", 1)
    size = arguments.get("size", 10)
    
    # Resolve region code
    region_code = region
    if not region.isdigit():
        # Try to find region code by name
        region_lower = region.lower()
        found = False
        for name, code in REGION_CODES.items():
            if region_lower in name.lower():
                region_code = code
                found = True
                break
        
        if not found:
            return [TextContent(
                type="text",
                text=f"지역을 찾을 수 없습니다: {region}\n\n사용 가능한 지역: {', '.join(list(REGION_CODES.keys())[:20])}..."
            )]
    
    # Validate inputs
    try:
        request = SearchRequest(
            region_code=region_code,
            year_month=year_month,
            page=page,
            size=size
        )
    except ValueError as e:
        return [TextContent(
            type="text",
            text=f"입력값 오류: {str(e)}"
        )]
    
    # Call API
    async with ApartmentTradeAPIClient() as client:
        try:
            data = await client.search_by_region(
                region_code=request.region_code,
                year_month=request.year_month,
                page=request.page,
                size=request.size
            )
            
            # Parse response
            response = ApartmentTradeResponse(**data)
            
            # Format results
            if not response.trade_items:
                return [TextContent(
                    type="text",
                    text=f"거래 정보가 없습니다.\n지역코드: {request.region_code}, 거래년월: {request.year_month}"
                )]
            
            # Build result text
            result_lines = [
                f"## 아파트 매매 실거래가 검색 결과",
                f"- 지역코드: {request.region_code}",
                f"- 거래년월: {request.year_month}",
                f"- 전체 건수: {response.total_count or len(response.trade_items)}",
                f"- 페이지: {response.page_no}/{(response.total_count or 0) // (response.num_of_rows or 10) + 1}",
                "",
                "### 거래 내역"
            ]
            
            for i, item in enumerate(response.trade_items, 1):
                deal_date = item.deal_date or f"{item.deal_year}-{item.deal_month}-{item.deal_day}"
                deal_amount = item.deal_amount_int
                
                result_lines.extend([
                    f"\n**{i}. {item.apt_nm or '아파트명 없음'}**",
                    f"- 주소: {item.umd_nm or ''} {item.jibun or ''}",
                    f"- 거래일: {deal_date}",
                    f"- 거래금액: {deal_amount:,}만원" if deal_amount else f"- 거래금액: {item.deal_amount}",
                    f"- 전용면적: {item.exclu_use_ar}㎡" if item.exclu_use_ar else "",
                    f"- 층: {item.floor}층" if item.floor else "",
                    f"- 건축년도: {item.build_year}년" if item.build_year else "",
                ])
                
                if item.apt_dong:
                    result_lines.append(f"- 동: {item.apt_dong}")
                
                if item.estate_agent_sgg_nm:
                    result_lines.append(f"- 중개사무소: {item.estate_agent_sgg_nm}")
            
            if response.has_more:
                result_lines.extend([
                    "",
                    f"*더 많은 결과를 보려면 page를 {request.page + 1}로 설정하세요.*"
                ])
            
            return [TextContent(
                type="text",
                text="\n".join(result_lines)
            )]
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return [TextContent(
                type="text",
                text=f"API 호출 실패: {str(e)}"
            )]


async def get_region_codes(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get region codes for Korean cities and districts"""
    
    search = arguments.get("search", "").lower()
    
    if search:
        # Filter regions by search term
        matched = {}
        for name, code in REGION_CODES.items():
            if search in name.lower():
                matched[name] = code
        
        if not matched:
            return [TextContent(
                type="text",
                text=f"'{search}'에 해당하는 지역을 찾을 수 없습니다."
            )]
        
        # Format results
        result_lines = [
            f"## '{search}' 검색 결과 ({len(matched)}개)",
            ""
        ]
        
        for name, code in sorted(matched.items()):
            result_lines.append(f"- **{name}**: {code}")
        
    else:
        # Show all major regions
        result_lines = [
            "## 한국 주요 지역코드",
            "",
            "### 특별시/광역시"
        ]
        
        # Major cities
        major_cities = [
            ("서울", "11000"),
            ("부산", "26000"),
            ("대구", "27000"),
            ("인천", "28000"),
            ("광주", "29000"),
            ("대전", "30000"),
            ("울산", "31000"),
            ("세종", "36110"),
        ]
        
        for name, code in major_cities:
            result_lines.append(f"- **{name}**: {code}")
        
        result_lines.extend([
            "",
            "### 서울특별시 구"
        ])
        
        # Seoul districts
        seoul_districts = [(k, v) for k, v in REGION_CODES.items() if "구" in k and v.startswith("111")]
        for name, code in seoul_districts[:10]:
            result_lines.append(f"- **{name}**: {code}")
        
        result_lines.extend([
            "",
            "### 경기도 주요 도시"
        ])
        
        # Gyeonggi cities
        gyeonggi_cities = [
            ("수원시", "41110"),
            ("성남시", "41130"),
            ("안양시", "41170"),
            ("부천시", "41190"),
            ("고양시", "41280"),
            ("용인시", "41460"),
        ]
        
        for name, code in gyeonggi_cities:
            result_lines.append(f"- **{name}**: {code}")
        
        result_lines.extend([
            "",
            f"*전체 {len(REGION_CODES)}개 지역이 등록되어 있습니다. 특정 지역을 검색하려면 search 파라미터를 사용하세요.*"
        ])
    
    return [TextContent(
        type="text",
        text="\n".join(result_lines)
    )]


async def main():
    """Main entry point for the MCP server"""
    logger.info(f"Starting apartment-trade MCP server v{__version__}")
    
    # Check for API key
    if not os.getenv("API_KEY"):
        logger.error("API_KEY environment variable is required")
        logger.error("Get your API key from https://www.data.go.kr")
        exit(1)
    
    # Run the server
    async with stdio_server(mcp) as server:
        await server.run()


if __name__ == "__main__":
    asyncio.run(main())