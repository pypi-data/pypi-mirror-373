#!/usr/bin/env python3
"""MCP server for Korea apartment trade data from data.go.kr"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from .api_client import ApartmentTradeAPIClient
from .models import ApartmentTradeResponse, SearchRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version
__version__ = "1.0.1"

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
            description="아파트 매매 실거래가 검색 - mode 파라미터로 조회 방식을 선택할 수 있습니다.",
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
                    "mode": {
                        "type": "string",
                        "enum": ["stats", "page", "auto"],
                        "description": "조회 모드: 'stats'=건수/통계만, 'page'=페이지별 조회, 'auto'=자동 분할 조회 (기본값: auto)",
                        "default": "auto"
                    },
                    "page": {
                        "type": "integer",
                        "description": "페이지 번호 (mode='page'일 때 사용, 기본값: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "size": {
                        "type": "integer",
                        "description": "페이지당 건수 (mode='page'일 때 사용, 기본값: 100, 최대: 100)",
                        "default": 100,
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
    """Search apartment trade transactions with different modes"""
    
    # Extract arguments
    region = arguments.get("region", "")
    year_month = arguments.get("year_month", "")
    mode = arguments.get("mode", "auto")
    page = arguments.get("page", 1)
    size = arguments.get("size", 100)
    
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
    
    async with ApartmentTradeAPIClient() as client:
        try:
            # Mode: stats - 통계 정보만 조회
            if mode == "stats":
                # 첫 페이지만 조회하여 전체 건수 확인
                data = await client.search_by_region(
                    region_code=region_code,
                    year_month=year_month,
                    page=1,
                    size=10  # 샘플 데이터도 함께 조회
                )
                response = ApartmentTradeResponse(**data)
                
                # 디버깅: 샘플 데이터 확인
                if response.trade_items and len(response.trade_items) > 0:
                    sample_items = response.trade_items[:3]
                    logger.info(f"Sample data for {region_code} {year_month}:")
                    for item in sample_items:
                        logger.info(f"  - {item.apt_nm}: {item.deal_year}-{item.deal_month}-{item.deal_day}")
                total_count = response.total_count or 0
                total_pages = (total_count + 99) // 100  # 100개씩 나눔
                
                result_lines = [
                    f"## 아파트 매매 실거래가 통계",
                    f"- 지역코드: {region_code}",
                    f"- 거래년월: {year_month}",
                    f"- **전체 거래 건수: {total_count}건**",
                    f"- **페이지 수: {total_pages}페이지** (페이지당 100건)",
                    "",
                ]
                
                # 샘플 데이터 추가
                if response.trade_items and len(response.trade_items) > 0:
                    result_lines.extend([
                        "### 샘플 데이터 (처음 5건)",
                    ])
                    for i, item in enumerate(response.trade_items[:5], 1):
                        deal_date = f"{item.deal_year}-{item.deal_month or '00'}-{item.deal_day or '00'}"
                        deal_amount = item.deal_amount_int
                        price_str = f"{deal_amount:,}만원" if deal_amount else f"{item.deal_amount}만원"
                        result_lines.append(
                            f"{i}. **{item.apt_nm}** | {item.umd_nm} | {deal_date} | {price_str}"
                        )
                    result_lines.append("")
                
                result_lines.extend([
                    "### 조회 방법",
                    f"- 페이지별 조회: mode='page', page=1~{total_pages}",
                    "- 전체 자동 조회: mode='auto' (주의: 500건 이하만)"
                ])
                
                return [TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )]
            
            # Mode: page - 특정 페이지만 조회
            elif mode == "page":
                data = await client.search_by_region(
                    region_code=region_code,
                    year_month=year_month,
                    page=page,
                    size=size
                )
                response = ApartmentTradeResponse(**data)
                total_count = response.total_count or 0
                total_pages = (total_count + size - 1) // size
                items = response.trade_items
                
                if not items:
                    return [TextContent(
                        type="text",
                        text=f"페이지 {page}에 데이터가 없습니다."
                    )]
                
                # 페이지 정보와 함께 결과 반환
                result_lines = [
                    f"## 아파트 매매 실거래가 검색 결과 (페이지 {page}/{total_pages})",
                    f"- 지역코드: {region_code}",
                    f"- 거래년월: {year_month}",
                    f"- 전체 건수: {total_count}건",
                    f"- 현재 페이지: {page}/{total_pages}",
                    f"- 표시 건수: {len(items)}건",
                    "",
                    "### 거래 내역"
                ]
                
                for i, item in enumerate(items, (page-1)*size + 1):
                    deal_date = item.deal_date or f"{item.deal_year}-{item.deal_month}-{item.deal_day}"
                    deal_amount = item.deal_amount_int
                    
                    # 핵심 정보만 표시: 단지명, 거래일, 거래금액, 전용면적, 층, 건축년도
                    price_str = f"{deal_amount:,}만원" if deal_amount else f"{item.deal_amount}만원"
                    result_lines.append(
                        f"\n{i}. **{item.apt_nm or '아파트명 없음'}** | "
                        f"{deal_date} | {price_str} | {item.exclu_use_ar}㎡ | {item.floor}층 | {item.build_year}년"
                    )
                
                if page < total_pages:
                    result_lines.extend([
                        "",
                        f"*다음 페이지: page={page+1}*"
                    ])
                
                return [TextContent(
                    type="text",
                    text="\n".join(result_lines)
                )]
            
            # Mode: auto - 자동 분할 조회 (500건 이하만)
            else:  # mode == "auto"
                # 먼저 건수 확인
                data = await client.search_by_region(
                    region_code=region_code,
                    year_month=year_month,
                    page=1,
                    size=1
                )
                response = ApartmentTradeResponse(**data)
                total_count = response.total_count or 0
                
                # 500건 초과시 stats 모드로 전환
                if total_count > 500:
                    total_pages = (total_count + 99) // 100
                    result_lines = [
                        f"## 아파트 매매 실거래가 조회 결과",
                        f"- 지역코드: {region_code}",
                        f"- 거래년월: {year_month}",
                        f"- **전체 거래 건수: {total_count}건** (500건 초과)",
                        "",
                        "### ⚠️ 대용량 데이터 경고",
                        f"전체 {total_count}건의 데이터는 너무 커서 자동 조회할 수 없습니다.",
                        "",
                        "### 조회 방법",
                        f"1. **페이지별 조회** (권장):",
                        f"   - mode='page', page=1~{total_pages} (페이지당 100건)",
                        f"2. **통계만 확인**:",
                        f"   - mode='stats'",
                        "",
                        "예시: mode='page', page=1"
                    ]
                    
                    return [TextContent(
                        type="text",
                        text="\n".join(result_lines)
                    )]
                
                # 500건 이하는 전체 조회
                all_items = []
                current_page = 1
                page_size = 100
                
                while len(all_items) < total_count:
                    data = await client.search_by_region(
                        region_code=region_code,
                        year_month=year_month,
                        page=current_page,
                        size=page_size
                    )
                    response = ApartmentTradeResponse(**data)
                    
                    if not response.trade_items:
                        break
                    
                    all_items.extend(response.trade_items)
                    current_page += 1
                    
                    if current_page > 5:  # 안전장치
                        break
                
                # 전체 데이터 반환
                if not all_items:
                    return [TextContent(
                        type="text",
                        text=f"거래 정보가 없습니다.\n지역코드: {region_code}, 거래년월: {year_month}"
                    )]
                
                # Build result text
                result_lines = [
                    f"## 아파트 매매 실거래가 검색 결과",
                    f"- 지역코드: {region_code}",
                    f"- 거래년월: {year_month}",
                    f"- 전체 건수: {total_count}",
                    f"- 실제 가져온 건수: {len(all_items)}",
                    "",
                    "### 거래 내역"
                ]
                
                for i, item in enumerate(all_items, 1):
                    deal_date = item.deal_date or f"{item.deal_year}-{item.deal_month}-{item.deal_day}"
                    deal_amount = item.deal_amount_int
                    
                    # 핵심 정보만 표시: 단지명, 거래일, 거래금액, 전용면적, 층, 건축년도
                    price_str = f"{deal_amount:,}만원" if deal_amount else f"{item.deal_amount}만원"
                    result_lines.append(
                        f"\n{i}. **{item.apt_nm or '아파트명 없음'}** | "
                        f"{deal_date} | {price_str} | {item.exclu_use_ar}㎡ | {item.floor}층 | {item.build_year}년"
                    )
                
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


async def run_server():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="data-go-mcp.apartment-trade",
                server_version=__version__,
                capabilities=mcp.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main():
    """Main entry point for the MCP server"""
    import sys
    
    logger.info(f"Starting apartment-trade MCP server v{__version__}")
    
    # Check for API key
    if not os.getenv("API_KEY"):
        logger.error("API_KEY environment variable is required")
        logger.error("Get your API key from https://www.data.go.kr")
        sys.exit(1)
    
    logger.info(f"API key configured: {os.getenv('API_KEY')[:10]}...")
    
    # Run the server
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
