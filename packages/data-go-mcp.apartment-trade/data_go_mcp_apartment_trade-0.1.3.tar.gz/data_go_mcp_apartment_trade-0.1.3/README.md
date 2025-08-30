# 국토교통부 아파트 매매 실거래가 MCP Server

국토교통부의 아파트 매매 실거래가 데이터를 조회할 수 있는 MCP (Model Context Protocol) 서버입니다.

## 🎯 주요 기능

- **아파트 매매 실거래가 검색**: 지역코드와 거래년월로 실거래 정보 조회
- **지역코드 조회**: 한국의 시/군/구 지역코드 검색 및 조회
- **상세 정보 제공**: 거래금액, 전용면적, 층수, 건축년도 등 상세 정보

## 📦 설치

### PyPI를 통한 설치 (권장)

```bash
pip install data-go-mcp.apartment-trade
```

또는 `uvx`를 사용한 실행:

```bash
uvx data-go-mcp.apartment-trade@latest
```

### 소스에서 설치

```bash
git clone https://github.com/Koomook/data-go-mcp-servers.git
cd data-go-mcp-servers/src/apartment-trade
uv sync
```

## 🔑 API 키 발급

1. [data.go.kr](https://www.data.go.kr) 회원가입
2. [국토교통부 아파트매매 실거래가](https://www.data.go.kr/data/15126500/openapi.do) API 신청
3. 발급받은 API 키를 환경변수로 설정:

```bash
export API_KEY="your-api-key-here"
```

## 🚀 사용법

### Claude Desktop 설정

`claude_desktop_config.json`에 다음 설정 추가:

```json
{
  "mcpServers": {
    "apartment-trade": {
      "command": "uvx",
      "args": ["data-go-mcp.apartment-trade@latest"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 로컬 개발 환경 설정

```json
{
  "mcpServers": {
    "apartment-trade": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "-m",
        "data_go_mcp.apartment_trade.server"
      ],
      "cwd": "/path/to/data-go-mcp-servers/src/apartment-trade",
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🛠️ 제공 도구

### 1. search_apartment_trades

아파트 매매 실거래가를 검색합니다.

**파라미터:**
- `region` (필수): 지역명 또는 지역코드 (예: "강남구", "11680")
- `year_month` (필수): 거래년월 YYYYMM 형식 (예: "202401")
- `page` (선택): 페이지 번호 (기본값: 1)
- `size` (선택): 페이지당 결과 수 (기본값: 10, 최대: 100)

**사용 예시:**
```
"2024년 1월 강남구의 아파트 매매 실거래가를 조회해줘"
"서울 송파구 202312 아파트 거래 내역 보여줘"
"지역코드 11680으로 2024년 상반기 거래 검색"
```

### 2. get_region_codes

한국의 시/군/구 지역코드를 조회합니다.

**파라미터:**
- `search` (선택): 검색할 지역명

**사용 예시:**
```
"서울의 모든 구 지역코드 알려줘"
"경기도 지역코드 목록 보여줘"
"강남 관련 지역코드 검색"
```

## 📊 응답 데이터 형식

### 거래 정보 필드

- `sgg_cd`: 시군구 코드
- `umd_nm`: 법정동 이름
- `apt_nm`: 아파트 이름
- `apt_dong`: 아파트 동 정보
- `jibun`: 지번
- `exclu_use_ar`: 전용면적 (㎡)
- `floor`: 층
- `deal_year/month/day`: 거래 날짜
- `deal_amount`: 거래금액 (만원)
- `build_year`: 건축년도
- `estate_agent_sgg_nm`: 중개사무소 시군구명
- `rgst_date`: 등록일

## 🏙️ 지원 지역

### 특별시/광역시
- 서울특별시 (11000) 및 25개 구
- 부산광역시 (26000) 및 16개 구/군
- 대구광역시 (27000) 및 8개 구/군
- 인천광역시 (28000) 및 10개 구/군
- 광주광역시 (29000) 및 5개 구
- 대전광역시 (30000) 및 5개 구
- 울산광역시 (31000) 및 5개 구/군
- 세종특별자치시 (36110)

### 경기도 주요 도시
- 수원시, 성남시, 안양시, 부천시, 고양시, 용인시 등 31개 시

## 🧪 테스트

```bash
# 단위 테스트 실행
cd src/apartment-trade
uv run pytest tests/

# 커버리지 포함
uv run pytest tests/ --cov=data_go_mcp.apartment_trade
```

## 📝 라이선스

Apache License 2.0

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](../../CONTRIBUTING.md)를 참조하세요.

## 🐛 문제 신고

이슈는 [GitHub Issues](https://github.com/Koomook/data-go-mcp-servers/issues)에 등록해주세요.

## 📚 관련 문서

- [data.go.kr API 문서](https://www.data.go.kr/data/15126500/openapi.do)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [프로젝트 홈페이지](https://github.com/Koomook/data-go-mcp-servers)