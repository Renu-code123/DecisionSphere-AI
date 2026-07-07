from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "citizen"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Community Schemas ---
class CommunityBase(BaseModel):
    name: str
    region_code: str
    population: int = 1000

class CommunityCreate(CommunityBase):
    pass

class CommunityResponse(CommunityBase):
    id: int
    risk_score: float
    health_index: float
    weather_summary: str
    traffic_status: str
    air_quality_index: int
    water_consumption: float
    energy_consumption: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Prediction Schemas ---
class PredictionCreate(BaseModel):
    community_id: int
    target_metric: str
    input_features: Optional[Dict[str, Any]] = None
    predicted_value: float
    confidence_score: float
    explanation: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    community_id: int
    target_metric: str
    input_features: Optional[Dict[str, Any]] = None
    predicted_value: float
    confidence_score: float
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ModelSliderInput(BaseModel):
    flood_risk_factor: float = Field(0.5, ge=0.0, le=1.0)
    traffic_congestion_factor: float = Field(0.5, ge=0.0, le=1.0)
    industrial_activity: float = Field(0.5, ge=0.0, le=1.0)
    disease_spread_rate: float = Field(0.1, ge=0.0, le=1.0)
    crime_density: float = Field(0.3, ge=0.0, le=1.0)
    temperature: float = Field(25.0, ge=-20.0, le=50.0)
    humidity: float = Field(50.0, ge=0.0, le=100.0)

# --- Report Schemas ---
class ReportCreate(BaseModel):
    title: str
    report_type: str
    file_path: str
    format: str = "PDF"

class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    file_path: str
    format: str
    created_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertCreate(BaseModel):
    community_id: int
    severity: str
    category: str
    message: str

class AlertResponse(BaseModel):
    id: int
    community_id: int
    severity: str
    category: str
    message: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Feedback Schemas ---
class FeedbackCreate(BaseModel):
    prediction_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Audit Log Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    ip_address: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# --- File Upload Schemas ---
class UploadedFileResponse(BaseModel):
    id: int
    file_name: str
    file_size: int
    content_type: str
    analysis_result: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Multi-Agent Communication ---
class AgentQueryRequest(BaseModel):
    query: str
    community_id: Optional[int] = 1

class AgentStepInfo(BaseModel):
    agent_name: str
    action_taken: str
    result_summary: str
    timestamp: datetime

class AgentQueryResponse(BaseModel):
    query: str
    coordinator_response: str
    steps: List[AgentStepInfo]
    recommendations: List[str]
    predictions: Dict[str, float]
    visualization_data: Dict[str, Any]
    alerts_triggered: List[Dict[str, Any]]
