"""Data models for apartment trade API"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class ApartmentTradeItem(BaseModel):
    """Individual apartment trade record"""
    
    # 시군구 코드
    sgg_cd: Optional[str] = Field(None, alias="sggCd", description="시군구 코드")
    
    # 법정동
    umd_nm: Optional[str] = Field(None, alias="umdNm", description="법정동 이름")
    
    # 아파트 정보
    apt_nm: Optional[str] = Field(None, alias="aptNm", description="아파트 이름")
    apt_dong: Optional[str] = Field(None, alias="aptDong", description="아파트 동 정보")
    jibun: Optional[str] = Field(None, alias="jibun", description="지번")
    
    # 면적 및 층수
    exclu_use_ar: Optional[str] = Field(None, alias="excluUseAr", description="전용면적")
    floor: Optional[str] = Field(None, alias="floor", description="층")
    
    # 거래 정보
    deal_year: Optional[str] = Field(None, alias="dealYear", description="거래년도")
    deal_month: Optional[str] = Field(None, alias="dealMonth", description="거래월")
    deal_day: Optional[str] = Field(None, alias="dealDay", description="거래일")
    deal_amount: Optional[str] = Field(None, alias="dealAmount", description="거래금액")
    
    # 건축 정보
    build_year: Optional[str] = Field(None, alias="buildYear", description="건축년도")
    
    # 거래 유형
    cdeal_type: Optional[str] = Field(None, alias="cdealType", description="거래유형")
    cdeal_day: Optional[str] = Field(None, alias="cdealDay", description="해제사유발생일")
    dealing_gbn: Optional[str] = Field(None, alias="dealingGbn", description="거래유형")
    
    # 중개사 정보
    estate_agent_sgg_nm: Optional[str] = Field(None, alias="estateAgentSggNm", description="중개사무소 시군구명")
    
    # 등록일
    rgst_date: Optional[str] = Field(None, alias="rgstDate", description="등록일")
    
    # 매도/매수자 구분
    sler_gbn: Optional[str] = Field(None, alias="slerGbn", description="매도자 구분")
    buyer_gbn: Optional[str] = Field(None, alias="buyerGbn", description="매수자 구분")
    
    # 토지 임대 구분
    land_leasehold_gbn: Optional[str] = Field(None, alias="landLeaseholdGbn", description="토지 임대 구분")
    
    model_config = {"populate_by_name": True}
    
    @field_validator("deal_amount")
    @classmethod
    def clean_deal_amount(cls, v: Optional[str]) -> Optional[str]:
        """Remove commas and whitespace from deal amount"""
        if v:
            return v.strip().replace(",", "")
        return v
    
    @property
    def deal_date(self) -> Optional[str]:
        """Get formatted deal date as YYYY-MM-DD"""
        if self.deal_year and self.deal_month and self.deal_day:
            return f"{self.deal_year}-{self.deal_month.zfill(2)}-{self.deal_day.zfill(2)}"
        return None
    
    @property
    def deal_amount_int(self) -> Optional[int]:
        """Get deal amount as integer (in 10,000 won units)"""
        if self.deal_amount:
            try:
                return int(self.deal_amount)
            except (ValueError, TypeError):
                return None
        return None
    
    @property
    def exclu_use_ar_float(self) -> Optional[float]:
        """Get exclusive use area as float"""
        if self.exclu_use_ar:
            try:
                return float(self.exclu_use_ar)
            except (ValueError, TypeError):
                return None
        return None


class ApartmentTradeItems(BaseModel):
    """Container for apartment trade items"""
    item: Union[ApartmentTradeItem, List[ApartmentTradeItem], None] = Field(None, description="거래 항목")
    
    @field_validator("item")
    @classmethod
    def ensure_list(cls, v):
        """Ensure item is always a list"""
        if v is None:
            return []
        if not isinstance(v, list):
            return [v]
        return v
    
    @property
    def items(self) -> List[ApartmentTradeItem]:
        """Get items as list"""
        if self.item is None:
            return []
        if isinstance(self.item, list):
            return self.item
        return [self.item]


class ApartmentTradeResponse(BaseModel):
    """API response for apartment trade data"""
    
    items: Optional[ApartmentTradeItems] = Field(None, description="거래 데이터")
    total_count: Optional[int] = Field(None, alias="totalCount", description="전체 건수")
    num_of_rows: Optional[int] = Field(None, alias="numOfRows", description="한 페이지 결과 수")
    page_no: Optional[int] = Field(None, alias="pageNo", description="페이지 번호")
    
    model_config = {"populate_by_name": True}
    
    @property
    def trade_items(self) -> List[ApartmentTradeItem]:
        """Get list of trade items"""
        if self.items:
            return self.items.items
        return []
    
    @property
    def has_more(self) -> bool:
        """Check if there are more pages"""
        if self.total_count and self.page_no and self.num_of_rows:
            return self.page_no * self.num_of_rows < self.total_count
        return False


class SearchRequest(BaseModel):
    """Request model for searching apartment trades"""
    
    region_code: str = Field(description="지역코드 (법정동코드 앞 5자리)")
    year_month: str = Field(description="계약년월 (YYYYMM format)")
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")
    
    @field_validator("region_code")
    @classmethod
    def validate_region_code(cls, v: str) -> str:
        """Validate region code format"""
        v = v.strip()
        if not v.isdigit() or len(v) != 5:
            raise ValueError("Region code must be 5 digits (e.g., '11110' for 서울 종로구)")
        return v
    
    @field_validator("year_month")
    @classmethod
    def validate_year_month(cls, v: str) -> str:
        """Validate year-month format"""
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Year-month must be 6 digits in YYYYMM format (e.g., '202401')")
        
        # Validate year and month ranges
        try:
            year = int(v[:4])
            month = int(v[4:6])
            
            if year < 2006 or year > datetime.now().year:
                raise ValueError(f"Year must be between 2006 and {datetime.now().year}")
            
            if month < 1 or month > 12:
                raise ValueError("Month must be between 01 and 12")
        except ValueError as e:
            raise ValueError(f"Invalid year-month format: {str(e)}")
        
        return v