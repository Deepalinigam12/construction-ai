"""Strict JSON contracts shared by the AI layer and the React UI."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

Level = Literal["low", "medium", "high", "critical"]
Source = Literal["ai", "demo"]


class Hazard(BaseModel):
    name: str
    severity: Level
    description: str
    corrective_action: str


class SafetyResult(BaseModel):
    summary: str
    risk_level: Level
    hazards: list[Hazard] = []
    ppe_issues: list[str] = []
    recommendations: list[str] = []
    source: Source = "ai"


class CrackResult(BaseModel):
    crack_type: str  # e.g. hairline, shrinkage, settlement, structural shear
    severity: Level
    width_estimate: str
    probable_causes: list[str] = []
    recommended_actions: list[str] = []
    urgent: bool = False
    summary: str = ""
    source: Source = "ai"


class PlanRequest(BaseModel):
    project_type: Literal["residential", "commercial"] = "residential"
    built_area_sqft: float = Field(gt=100, le=1_000_000)
    floors: int = Field(1, ge=1, le=30)
    quality: Literal["basic", "standard", "premium"] = "standard"
    city_cost_factor: float = Field(1.0, gt=0.3, le=3.0)


class MaterialLine(BaseModel):
    item: str
    quantity: float
    unit: str
    est_cost: float


class Phase(BaseModel):
    phase: str
    start_week: int
    duration_weeks: int
    tasks: list[str]


class PlanResult(BaseModel):
    materials: list[MaterialLine]
    material_cost: float
    labour_and_finishing_cost: float
    total_cost: float
    cost_per_sqft: float
    schedule: list[Phase]
    total_weeks: int
    ai_notes: list[str] = []
    source: Source = "demo"


class ValuationRequest(BaseModel):
    location: str = "Indore"
    property_type: Literal["apartment", "house", "villa", "commercial", "plot"] = "apartment"
    area_sqft: float = Field(gt=50, le=1_000_000)
    age_years: int = Field(0, ge=0, le=100)
    bedrooms: int = Field(2, ge=0, le=12)
    condition: Literal["poor", "average", "good", "excellent"] = "good"
    amenities: list[str] = []
    base_rate_per_sqft: Optional[float] = Field(None, gt=0)


class Factor(BaseModel):
    name: str
    impact_pct: float


class ValuationResult(BaseModel):
    estimated_value: float
    low: float
    high: float
    price_per_sqft: float
    factors: list[Factor]
    summary: str
    source: Source = "demo"


class Narrative(BaseModel):
    summary: str
    notes: list[str] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = []
    city: Optional[str] = None


class ChatReply(BaseModel):
    answer: str
    suggestions: list[str] = []
    source: Source = "ai"


class WeatherAdvisory(BaseModel):
    city: str
    temperature_c: float
    wind_kmh: float
    rain_mm_next_24h: float
    rain_probability_pct: float
    forecast_days: list[dict]
    advisories: list[str]
    go_no_go: Literal["go", "caution", "no-go"]
