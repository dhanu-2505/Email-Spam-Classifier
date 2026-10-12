from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
    message: str = Field(..., min_length=1, max_length=5000)


class BatchPredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
    messages: List[str] = Field(..., min_length=1, max_length=50)


class PredictResponse(BaseModel):
    label: str
    confidence: Optional[float] = None
    explanation: str
    top_features: List[str] = []


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    model_loaded: bool
    backend: str


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
