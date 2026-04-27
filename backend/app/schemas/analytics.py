from pydantic import BaseModel
from typing import List

class ModelMetrics(BaseModel):
    r2_score: float
    rmse: float
    mae: float
    last_trained: str

class FeatureImportance(BaseModel):
    feature: str
    importance: float

class DistributionData(BaseModel):
    city: str
    count: int
    avg_price: float

class MarketSegment(BaseModel):
    cluster_name: str
    count: int
    description: str
    color: str