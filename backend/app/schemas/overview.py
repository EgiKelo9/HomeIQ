from typing import Optional
from pydantic import BaseModel

class OverviewMetric(BaseModel):
    key: str
    label: str
    value: float
    formatted_value: str
    note: Optional[str] = None


class CityPricePoint(BaseModel):
    city: str
    average_price: float
    listing_count: int
    formatted_average_price: str


class OverviewResponse(BaseModel):
    total_listings: int
    average_price: float
    median_price: float
    max_price: float
    cards: list[OverviewMetric]
    chart: list[CityPricePoint]
    last_updated: Optional[str] = None
