from pydantic import BaseModel

class TrainResponse(BaseModel):
    message: str
    status: str

class PredictRequest(BaseModel):
    bedrooms: float
    bathrooms: float
    building_size_m2: float
    land_size_m2: float
    city: str
    district: str

class PredictResponse(BaseModel):
    predicted_price: float